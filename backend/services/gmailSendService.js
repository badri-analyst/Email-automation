/**
 * Send emails via the Gmail REST API (HTTPS) instead of nodemailer SMTP.
 * SMTP (ports 465/587) is blocked on many cloud platforms (e.g. Render).
 * The Gmail API uses port 443 which is always open.
 */

const DEFAULT_RETRIES = 2;

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Build a RFC 2822 email message and base64url-encode it for the Gmail API.
 */
function encodeSubject(subject) {
  // RFC 2047 UTF-8 encoded word — prevents garbled characters (em dashes, accents, etc.)
  return `=?UTF-8?B?${Buffer.from(String(subject || '')).toString('base64')}?=`;
}

function buildRawMessage({ from, to, subject, body, attachment = null }) {
  const plain = String(body || '').trim();
  const html = plain
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>');

  const outerBoundary = `outer_${Date.now()}`;
  const innerBoundary = `inner_${Date.now() + 1}`;

  let message;

  if (attachment) {
    // multipart/mixed wraps body alternatives + attachment
    message = [
      `From: ${from}`,
      `To: ${to}`,
      `Subject: ${encodeSubject(subject)}`,
      'MIME-Version: 1.0',
      `Content-Type: multipart/mixed; boundary="${outerBoundary}"`,
      '',
      `--${outerBoundary}`,
      `Content-Type: multipart/alternative; boundary="${innerBoundary}"`,
      '',
      `--${innerBoundary}`,
      'Content-Type: text/plain; charset="UTF-8"',
      '',
      plain,
      '',
      `--${innerBoundary}`,
      'Content-Type: text/html; charset="UTF-8"',
      '',
      `<html><body>${html}</body></html>`,
      '',
      `--${innerBoundary}--`,
      '',
      `--${outerBoundary}`,
      `Content-Type: ${attachment.mimeType}; name="${attachment.filename}"`,
      'Content-Transfer-Encoding: base64',
      `Content-Disposition: attachment; filename="${attachment.filename}"`,
      '',
      attachment.buffer.toString('base64').match(/.{1,76}/g).join('\r\n'),
      '',
      `--${outerBoundary}--`,
    ].join('\r\n');
  } else {
    // simple multipart/alternative — no attachment
    message = [
      `From: ${from}`,
      `To: ${to}`,
      `Subject: ${encodeSubject(subject)}`,
      'MIME-Version: 1.0',
      `Content-Type: multipart/alternative; boundary="${outerBoundary}"`,
      '',
      `--${outerBoundary}`,
      'Content-Type: text/plain; charset="UTF-8"',
      '',
      plain,
      '',
      `--${outerBoundary}`,
      'Content-Type: text/html; charset="UTF-8"',
      '',
      `<html><body>${html}</body></html>`,
      '',
      `--${outerBoundary}--`,
    ].join('\r\n');
  }

  return Buffer.from(message)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

/**
 * Use a stored refresh token to get a fresh Gmail access token.
 */
async function getAccessToken(refreshToken) {
  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  if (!clientId || !clientSecret) {
    throw new Error('GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET is not configured on the server.');
  }

  const body = new URLSearchParams({
    refresh_token: refreshToken,
    client_id: clientId,
    client_secret: clientSecret,
    grant_type: 'refresh_token',
  });

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15_000);
  let res;
  try {
    res = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timer);
  }

  const json = await res.json();
  if (!res.ok || !json.access_token) {
    throw new Error(`Token refresh failed: ${json.error_description || json.error || res.status}`);
  }
  return json.access_token;
}

/**
 * Send one email via the Gmail REST API.
 */
async function sendViaGmailApi({ accessToken, gmailAddress, to, subject, body, attachment }) {
  const raw = buildRawMessage({ from: gmailAddress, to, subject, body, attachment });

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20_000);
  let res;
  try {
    res = await fetch('https://gmail.googleapis.com/gmail/v1/users/me/messages/send', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ raw }),
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timer);
  }

  const json = await res.json();
  if (!res.ok) {
    const detail = json?.error?.message || JSON.stringify(json);
    throw new Error(`Gmail API ${res.status}: ${detail}`);
  }
  return json.id; // Gmail message ID
}

/**
 * Send an email via Gmail OAuth2 REST API with retry.
 *
 * @param {object} opts
 * @param {string} opts.gmailAddress  - sender Gmail address
 * @param {string} opts.refreshToken  - stored OAuth2 refresh token
 * @param {string} opts.to            - recipient address
 * @param {string} opts.subject
 * @param {string} opts.body
 * @param {number} [opts.retries]
 */
export async function sendEmailWithRetry({ gmailAddress, refreshToken, to, subject, body, attachment = null, retries = DEFAULT_RETRIES }) {
  if (!gmailAddress || !refreshToken) {
    throw new Error('Gmail address and OAuth2 refresh token are required to send email.');
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(to || '').trim())) {
    throw new Error('Recipient email is missing or invalid.');
  }

  // Fetch access token once — valid for 1 hour, enough for all retries.
  const accessToken = await getAccessToken(refreshToken);

  let lastError;
  for (let attempt = 1; attempt <= retries + 1; attempt += 1) {
    try {
      const messageId = await sendViaGmailApi({
        accessToken,
        gmailAddress,
        to: String(to).trim().toLowerCase(),
        subject: String(subject || 'Quick note').trim(),
        body,
        attachment,
      });
      return {
        send_status: 'sent',
        provider_message_id: messageId || '',
        send_reason: 'Email sent via Gmail REST API.',
      };
    } catch (error) {
      lastError = error;
      if (attempt <= retries) await delay(400 * attempt);
    }
  }

  return {
    send_status: 'send_failed',
    provider_message_id: '',
    send_reason: lastError?.message || 'Email send failed.',
  };
}
