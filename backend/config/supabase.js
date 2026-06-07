import { createClient } from '@supabase/supabase-js';
import WebSocket from 'ws';

function validateSupabaseUrl(url) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'https:' && parsed.hostname.endsWith('.supabase.co');
  } catch (_error) {
    return false;
  }
}

async function fetchWithTimeout(input, init = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    return await fetch(input, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timeout);
  }
}

let _supabaseClient = null;

export function getSupabase() {
  if (_supabaseClient) return _supabaseClient;
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) return null;
  if (!validateSupabaseUrl(url)) {
    throw new Error('SUPABASE_URL must be a valid https://*.supabase.co URL.');
  }
  _supabaseClient = createClient(url, key, {
    auth: { persistSession: false },
    global: { fetch: fetchWithTimeout },
    realtime: { transport: WebSocket },
  });
  return _supabaseClient;
}

export { fetchWithTimeout };

export function getSupabaseSettings() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  return {
    url,
    keyConfigured: Boolean(key),
    urlValid: Boolean(url && validateSupabaseUrl(url)),
    host: url ? new URL(url).hostname : '',
  };
}
