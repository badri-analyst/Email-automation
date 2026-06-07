import crypto from 'crypto';
import nodemailer from 'nodemailer';
import { getSupabase } from '../config/supabase.js';

// ---------------------------------------------------------------------------
// Encryption helpers (AES-256-GCM)
// ---------------------------------------------------------------------------

function getEncryptionKey() {
  const raw = process.env.GMAIL_CREDENTIAL_ENCRYPTION_KEY || process.env.CREDENTIAL_ENCRYPTION_KEY;
  if (!raw) {
    if (process.env.NODE_ENV === 'production') {
      throw new Error('GMAIL_CREDENTIAL_ENCRYPTION_KEY is required in production.');
    }
    return crypto.createHash('sha256').update('local-development-only-key').digest();
  }

  if (/^[a-f0-9]{64}$/i.test(raw)) return Buffer.from(raw, 'hex');
  const decoded = Buffer.from(raw, 'base64');
  if (decoded.length === 32) return decoded;
  return crypto.createHash('sha256').update(raw).digest();
}

function encryptRefreshToken(secret) {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', getEncryptionKey(), iv);
  const encrypted = Buffer.concat([cipher.update(String(secret), 'utf8'), cipher.final()]);
  return {
    encrypted_refresh_token: encrypted.toString('base64'),
    encryption_iv: iv.toString('base64'),
    encryption_tag: cipher.getAuthTag().toString('base64'),
  };
}

function decryptRefreshToken(record) {
  // Supports both new column name (encrypted_refresh_token) and legacy
  // back-filled rows that still use encrypted_app_password.
  const ciphertext = record.encrypted_refresh_token || record.encrypted_app_password;
  const decipher = crypto.createDecipheriv(
    'aes-256-gcm',
    getEncryptionKey(),
    Buffer.from(record.encryption_iv, 'base64'),
  );
  decipher.setAuthTag(Buffer.from(record.encryption_tag, 'base64'));
  const decrypted = Buffer.concat([
    decipher.update(Buffer.from(ciphertext, 'base64')),
    decipher.final(),
  ]);
  return decrypted.toString('utf8');
}

// ---------------------------------------------------------------------------
// Google OAuth2 helpers
// ---------------------------------------------------------------------------

function getOAuthConfig() {
  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  if (!clientId || !clientSecret) {
    throw new Error('GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set.');
  }
  return { clientId, clientSecret };
}

/**
 * Decode the email claim from a Google id_token without verifying the
 * signature (signature verification requires fetching Google's public keys;
 * unnecessary here because the token was just issued to us directly by Google's
 * token endpoint over HTTPS).
 */
export function extractEmailFromIdToken(idToken) {
  try {
    const payload = idToken.split('.')[1];
    const json = JSON.parse(Buffer.from(payload, 'base64url').toString('utf8'));
    return typeof json.email === 'string' ? json.email.toLowerCase() : null;
  } catch {
    return null;
  }
}

/**
 * Exchange an authorization code for access + refresh tokens.
 * Returns accessToken, refreshToken, expiresIn, and gmailAddress decoded
 * from the id_token so callers always know which Gmail was authorized.
 */
export async function exchangeCodeForTokens(code, redirectUri) {
  const { clientId, clientSecret } = getOAuthConfig();
  const body = new URLSearchParams({
    code,
    client_id: clientId,
    client_secret: clientSecret,
    redirect_uri: redirectUri,
    grant_type: 'authorization_code',
  });

  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  });

  const json = await res.json();
  if (!res.ok || json.error) {
    throw new Error(`Google token exchange failed: ${json.error_description || json.error || res.status}`);
  }
  if (!json.refresh_token) {
    throw new Error(
      'No refresh_token returned. Ensure access_type=offline and prompt=consent are set in the OAuth URL.',
    );
  }

  const gmailAddress = json.id_token ? extractEmailFromIdToken(json.id_token) : null;

  return {
    accessToken: json.access_token,
    refreshToken: json.refresh_token,
    expiresIn: json.expires_in,
    gmailAddress,
  };
}

/**
 * Use a stored refresh token to obtain a fresh access token.
 */
export async function refreshAccessToken(refreshToken) {
  const { clientId, clientSecret } = getOAuthConfig();
  const body = new URLSearchParams({
    refresh_token: refreshToken,
    client_id: clientId,
    client_secret: clientSecret,
    grant_type: 'refresh_token',
  });

  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  });

  const json = await res.json();
  if (!res.ok || json.error) {
    throw new Error(`Google token refresh failed: ${json.error_description || json.error || res.status}`);
  }
  return json.access_token;
}

/**
 * Tell Google to invalidate a refresh token.
 * Failures are swallowed — we still soft-delete locally even if Google's
 * endpoint is unreachable.
 */
async function revokeTokenAtGoogle(refreshToken) {
  try {
    await fetch(`https://oauth2.googleapis.com/revoke?token=${encodeURIComponent(refreshToken)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  } catch {
    // Network failure — local revocation still proceeds.
  }
}

/**
 * Build a nodemailer transport authenticated via OAuth2 access token.
 */
export function createGmailOAuthTransport(gmailAddress, accessToken) {
  return nodemailer.createTransport({
    service: 'gmail',
    auth: {
      type: 'OAuth2',
      user: gmailAddress,
      accessToken,
    },
  });
}

/**
 * Verify the OAuth2 transport can connect to Gmail.
 */
export async function validateGmailOAuthCredentials(gmailAddress, accessToken) {
  const transporter = createGmailOAuthTransport(gmailAddress, accessToken);
  await transporter.verify();
  return { gmailAddress, status: 'valid' };
}

// ---------------------------------------------------------------------------
// New multi-account credential persistence (gmail_oauth_accounts table)
// ---------------------------------------------------------------------------

/**
 * Save (or overwrite) a Gmail OAuth2 credential for a user.
 * Uses upsert on (user_id, gmail_address) so reconnecting the same Gmail
 * simply refreshes the stored token.
 */
export async function saveGmailAccountCredential({ userId, userEmail, gmailAddress, refreshToken }) {
  if (!gmailAddress || !refreshToken) {
    throw new Error('gmailAddress and refreshToken are required.');
  }
  const normalized = String(gmailAddress).trim().toLowerCase();
  const encrypted = encryptRefreshToken(refreshToken);
  const supabase = getSupabase();

  if (!supabase) return { gmailAddress: normalized, status: 'stored' };

  const { error } = await supabase.from('gmail_oauth_accounts').upsert({
    user_id: userId,
    user_email: String(userEmail).trim().toLowerCase(),
    gmail_address: normalized,
    ...encrypted,
    is_active: true,
    revoked_at: null,
    updated_at: new Date().toISOString(),
  }, { onConflict: 'user_id,gmail_address' });

  if (error) {
    throw new Error(`Failed to save Gmail account credential: ${error.message}`);
  }

  return { gmailAddress: normalized, status: 'stored' };
}

/**
 * Return all active Gmail accounts connected by a user.
 * Each entry: { gmailAddress, connectedAt, updatedAt }
 */
export async function listGmailAccounts({ userId, userEmail }) {
  if (!userId && !userEmail) return [];
  const supabase = getSupabase();
  if (!supabase) return [];

  let query = supabase
    .from('gmail_oauth_accounts')
    .select('gmail_address, connected_at, updated_at')
    .eq('is_active', true)
    .order('connected_at', { ascending: true });

  // Prefer UUID lookup; fall back to email for back-filled sentinel rows.
  if (userId && userId !== '00000000-0000-0000-0000-000000000000') {
    query = query.eq('user_id', userId);
  } else if (userEmail) {
    query = query.eq('user_email', String(userEmail).trim().toLowerCase());
  }

  const { data, error } = await query;
  if (error) throw new Error(`Failed to list Gmail accounts: ${error.message}`);

  return (data || []).map((row) => ({
    gmailAddress: row.gmail_address,
    connectedAt: row.connected_at,
    updatedAt: row.updated_at,
  }));
}

/**
 * Load the decrypted refresh token for a specific Gmail address belonging to a user.
 * Returns { gmailAddress, refreshToken } or null if not found.
 */
export async function loadCredentialForAccount({ userId, userEmail, gmailAddress }) {
  if (!userId && !userEmail) return null;
  const supabase = getSupabase();
  if (!supabase) return null;

  const normalized = String(gmailAddress).trim().toLowerCase();

  let query = supabase
    .from('gmail_oauth_accounts')
    .select('*')
    .eq('gmail_address', normalized)
    .eq('is_active', true);

  if (userId && userId !== '00000000-0000-0000-0000-000000000000') {
    query = query.eq('user_id', userId);
  } else if (userEmail) {
    query = query.eq('user_email', String(userEmail).trim().toLowerCase());
  }

  const { data, error } = await query.maybeSingle();
  if (error) throw new Error(`Failed to load Gmail credential: ${error.message}`);
  if (!data) return null;

  return { gmailAddress: data.gmail_address, refreshToken: decryptRefreshToken(data) };
}

/**
 * Load the most recently connected active Gmail account for a user.
 * Used when no specific gmail_address was requested (single-account path).
 * Returns { gmailAddress, refreshToken } or null.
 */
export async function loadLatestCredential({ userId, userEmail }) {
  if (!userId && !userEmail) return null;
  const supabase = getSupabase();
  if (!supabase) return null;

  let query = supabase
    .from('gmail_oauth_accounts')
    .select('*')
    .eq('is_active', true)
    .order('updated_at', { ascending: false })
    .limit(1);

  if (userId && userId !== '00000000-0000-0000-0000-000000000000') {
    query = query.eq('user_id', userId);
  } else if (userEmail) {
    query = query.eq('user_email', String(userEmail).trim().toLowerCase());
  }

  const { data, error } = await query.maybeSingle();
  if (error) throw new Error(`Failed to load latest Gmail credential: ${error.message}`);
  if (!data) return null;

  return { gmailAddress: data.gmail_address, refreshToken: decryptRefreshToken(data) };
}

/**
 * Disconnect a Gmail account: revoke the token at Google, then soft-delete
 * the row by setting is_active = false and revoked_at = now().
 * Returns { gmailAddress, status: 'revoked' } or throws on DB error.
 */
export async function revokeGmailAccount({ userId, userEmail, gmailAddress }) {
  if (!userId && !userEmail) throw new Error('User identity is required to revoke a Gmail account.');
  const supabase = getSupabase();
  if (!supabase) throw new Error('Database is not configured.');

  const normalized = String(gmailAddress).trim().toLowerCase();

  // Load the refresh token so we can revoke it at Google.
  const credential = await loadCredentialForAccount({ userId, userEmail, gmailAddress: normalized });
  if (credential?.refreshToken) {
    await revokeTokenAtGoogle(credential.refreshToken);
  }

  let query = supabase
    .from('gmail_oauth_accounts')
    .update({ is_active: false, revoked_at: new Date().toISOString(), updated_at: new Date().toISOString() })
    .eq('gmail_address', normalized);

  if (userId && userId !== '00000000-0000-0000-0000-000000000000') {
    query = query.eq('user_id', userId);
  } else if (userEmail) {
    query = query.eq('user_email', String(userEmail).trim().toLowerCase());
  }

  const { error } = await query;
  if (error) throw new Error(`Failed to revoke Gmail account: ${error.message}`);

  return { gmailAddress: normalized, status: 'revoked' };
}

