import {
  createGmailOAuthTransport,
  refreshAccessToken,
} from './gmailCredentialService.js';

const DEFAULT_RETRIES = 2;

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function plainTextToHtml(text = '') {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>');
}

/**
 * Send an email via Gmail OAuth2.
 *
 * @param {object} opts
 * @param {string} opts.gmailAddress  - sender Gmail address
 * @param {string} opts.refreshToken  - stored OAuth2 refresh token
 * @param {string} opts.to            - recipient address
 * @param {string} opts.subject
 * @param {string} opts.body
 * @param {number} [opts.retries]
 */
export async function sendEmailWithRetry({ gmailAddress, refreshToken, to, subject, body, retries = DEFAULT_RETRIES }) {
  if (!gmailAddress || !refreshToken) {
    throw new Error('Gmail address and OAuth2 refresh token are required to send email.');
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(to || '').trim())) {
    throw new Error('Recipient email is missing or invalid.');
  }

  // Obtain a fresh access token once before the retry loop.
  // Access tokens are valid for 1 hour; retries happen within seconds so one
  // token is sufficient for the entire send attempt.
  const accessToken = await refreshAccessToken(refreshToken);

  let lastError;
  for (let attempt = 1; attempt <= retries + 1; attempt += 1) {
    try {
      const transporter = createGmailOAuthTransport(gmailAddress, accessToken);
      const result = await transporter.sendMail({
        from: gmailAddress,
        to: String(to).trim().toLowerCase(),
        subject: String(subject || 'Quick note').trim(),
        text: String(body || '').trim(),
        html: plainTextToHtml(body),
      });
      return {
        send_status: 'sent',
        provider_message_id: result.messageId,
        send_reason: 'Email sent through Gmail OAuth2.',
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
