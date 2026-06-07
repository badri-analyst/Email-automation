import { runPython } from '../utils/pythonBridge.js';
import { getSupabase, getSupabaseSettings, fetchWithTimeout } from '../config/supabase.js';
import { generateSafeJson } from '../services/aiJsonService.js';
import {
  exchangeCodeForTokens,
  saveGmailAccountCredential,
  listGmailAccounts,
  loadCredentialForAccount,
  loadLatestCredential,
  revokeGmailAccount,
} from '../services/gmailCredentialService.js';
import { sendEmailWithRetry } from '../services/gmailSendService.js';

const CAMPAIGN_STATUSES = {
  uploaded: 'Uploaded',
  processing: 'Processing',
  completed: 'Completed',
  failed: 'Failed',
  partiallyCompleted: 'Partially Completed',
  noRecipients: 'No Recipients',
};

export async function health(_request, response) {
  response.json({
    status: 'ok',
    service: 'ai-outreach-backend',
    supabaseConfigured: Boolean(process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY),
    roleCountryApiConfigured: Boolean(process.env.ROLE_COUNTRY_API_KEY),
    linkedinResearchApiConfigured: Boolean(process.env.LINKEDIN_RESEARCH_API_KEY),
    companyResearchApiConfigured: Boolean(process.env.COMPANY_RESEARCH_API_KEY),
    communicationSignalApiConfigured: Boolean(process.env.COMMUNICATION_SIGNAL_API_KEY),
    emailWritingApiConfigured: Boolean(process.env.EMAIL_WRITING_API_KEY || process.env.OPENAI_API_KEY),
    sharedAiConfigured: Boolean(process.env.AI_API_KEY || process.env.AIMLAPI_API_KEY || process.env.OPENAI_API_KEY),
    gmailAuthMode: 'oauth2',
  });
}

function supabaseWriteError(context, error) {
  const details = [
    error?.message,
    error?.details,
    error?.hint,
    error?.code,
  ].filter(Boolean).join(' ');
  return new Error(`${context}. Check SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, and table migrations in Render/Supabase. ${details}`.trim());
}

function safeErrorDetails(error) {
  return {
    message: error?.message || 'Unknown error',
    name: error?.name || '',
    causeCode: error?.cause?.code || '',
    causeName: error?.cause?.name || '',
    causeMessage: error?.cause?.message || '',
  };
}

async function assertSupabaseWrite(result, context) {
  if (result?.error) {
    throw supabaseWriteError(context, result.error);
  }
  return result;
}

async function getAuthenticatedUser(request) {
  const token = String(request.headers.authorization || '').replace(/^Bearer\s+/i, '').trim();
  if (!token) {
    const error = new Error('Authentication is required.');
    error.status = 401;
    throw error;
  }

  const supabase = getSupabase();
  if (!supabase) {
    const error = new Error('Supabase authentication is not configured.');
    error.status = 503;
    throw error;
  }

  const { data, error } = await supabase.auth.getUser(token);
  if (error || !data?.user?.email) {
    const authError = new Error('Invalid or expired session. Please sign in again.');
    authError.status = 401;
    throw authError;
  }

  return {
    id: data.user.id,
    email: data.user.email.toLowerCase(),
    name: data.user.user_metadata?.full_name || data.user.user_metadata?.name || data.user.email,
  };
}

function campaignNameFromFile(filename = '') {
  return String(filename || 'New Campaign')
    .replace(/\.(csv|xlsx)$/i, '')
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim() || 'New Campaign';
}

function mapCampaign(record = {}) {
  return {
    id: record.id,
    userId: record.user_id,
    userEmail: record.user_email,
    campaignName: record.campaign_name,
    fileName: record.file_name,
    totalEmails: record.total_emails || 0,
    sentCount: record.sent_count || 0,
    failedCount: record.failed_count || 0,
    pendingCount: record.pending_count || 0,
    status: record.status,
    createdAt: record.created_at,
    updatedAt: record.updated_at,
  };
}

function statusFromCounts(totalEmails, sentCount, failedCount, pendingCount) {
  if (totalEmails === 0) return CAMPAIGN_STATUSES.noRecipients;
  if (pendingCount > 0) return CAMPAIGN_STATUSES.processing;
  if (totalEmails > 0 && sentCount === totalEmails) return CAMPAIGN_STATUSES.completed;
  if (totalEmails > 0 && failedCount === totalEmails) return CAMPAIGN_STATUSES.failed;
  if (sentCount > 0 && failedCount > 0) return CAMPAIGN_STATUSES.partiallyCompleted;
  if (failedCount > 0) return CAMPAIGN_STATUSES.failed;
  return CAMPAIGN_STATUSES.completed;
}

function mapCampaignEmail(record = {}) {
  return {
    id: record.id,
    campaignId: record.campaign_id,
    recipientEmail: record.recipient_email,
    recipientName: record.recipient_name || '',
    companyName: record.company_name || '',
    subject: record.subject || '',
    emailBody: record.email_body || '',
    status: record.status,
    errorMessage: record.error_message || '',
    sentAt: record.sent_at,
    rowData: record.row_data || {},
  };
}

async function updateCampaignCounts({ campaignId, userEmail, totalEmails, sentCount, failedCount, status }) {
  const supabase = getSupabase();
  if (!supabase || !campaignId) return null;
  const pendingCount = Math.max((totalEmails || 0) - (sentCount || 0) - (failedCount || 0), 0);
  const nextStatus = status || statusFromCounts(totalEmails, sentCount, failedCount, pendingCount);
  const { data, error } = await supabase
    .from('campaigns')
    .update({
      total_emails: totalEmails,
      sent_count: sentCount,
      failed_count: failedCount,
      pending_count: pendingCount,
      status: nextStatus,
      updated_at: new Date().toISOString(),
    })
    .eq('id', campaignId)
    .eq('user_email', userEmail)
    .select('*')
    .maybeSingle();
  if (error) throw supabaseWriteError('Supabase campaign update failed', error);
  return data ? mapCampaign(data) : null;
}

async function recalculateCampaignFromEmails({ campaignId, userEmail, status }) {
  const supabase = getSupabase();
  if (!supabase) return null;
  const { data, error } = await supabase
    .from('campaign_emails')
    .select('status')
    .eq('campaign_id', campaignId)
    .eq('user_email', userEmail);
  if (error) throw supabaseWriteError('Supabase campaign email count failed', error);
  const totalEmails = data?.length || 0;
  const sentCount = (data || []).filter((record) => record.status === 'Sent').length;
  const failedCount = (data || []).filter((record) => record.status === 'Failed').length;
  return updateCampaignCounts({ campaignId, userEmail, totalEmails, sentCount, failedCount, status });
}

async function loadCandidateProfile(userEmail) {
  const supabase = getSupabase();
  if (!supabase) return {};
  const { data, error } = await supabase
    .from('candidate_assets_results')
    .select('structured_output')
    .eq('candidate_id', userEmail)
    .order('updated_at', { ascending: false })
    .limit(1)
    .maybeSingle();
  if (error) throw supabaseWriteError('Supabase candidate profile load failed', error);
  return data?.structured_output?.profile_form || {};
}

function debugLog(...args) {
  if (process.env.NODE_ENV !== 'production') {
    console.log(...args);
  }
}

function emailIsSendable(decisionOutput = {}, emailOutput = {}) {
  const generated = ['email_ready', 'fallback_email_created'].includes(emailOutput.email_generation_status);
  const hasContent = Boolean(String(emailOutput.subject_line || '').trim() && String(emailOutput.email_body || '').trim());
  const blockedActions = new Set(['skip_sending', 'skip_duplicate', 'manual_review', 'stop_processing']);
  const blockedStatuses = new Set([
    'blocked_invalid_email',
    'skipped_duplicate',
    'manual_review_required',
    'insufficient_data',
    'gmail_not_configured',
    'decision_failed',
  ]);
  return decisionOutput.email_send_permission === 'allowed'
    && !blockedActions.has(decisionOutput.next_action)
    && !blockedStatuses.has(decisionOutput.decision_status)
    && decisionOutput.manual_review_flag !== true
    && generated
    && hasContent;
}

function blockedSendResult(reason) {
  return {
    send_status: 'send_failed',
    provider_message_id: '',
    send_reason: reason,
  };
}

async function enhanceRoleCountry(input, fallback) {
  return generateSafeJson({
    moduleName: 'role_country',
    task: 'Produce role-country intelligence JSON for recruiter outreach using only the provided cleaned role, country, industry, seniority, and candidate positioning. Preserve the existing schema exactly.',
    input: { request: input, deterministic_output: fallback },
    schemaHint: 'RoleCountryOutput',
    fallback,
    temperature: 0.2,
    topP: 0.7,
    maxTokens: 1024,
  });
}

async function enhanceLinkedinResearch(input, fallback) {
  return generateSafeJson({
    moduleName: 'linkedin_research',
    task: 'Produce LinkedIn research JSON using only provided professional profile text, summaries, posts, and approved context. A LinkedIn URL alone is not evidence. Preserve the existing schema exactly.',
    input: { request: input, deterministic_output: fallback },
    schemaHint: 'LinkedInResearchOutput',
    fallback,
    temperature: 0.15,
    topP: 1,
    maxTokens: 2048,
  });
}

async function enhanceCompanyResearch(input, fallback) {
  return generateSafeJson({
    moduleName: 'company_research',
    task: 'Produce company research JSON using only provided company name, website URL, approved source snippets, and deterministic output. Do not invent company facts, hiring, funding, or news. Preserve the existing schema exactly.',
    input: { request: input, deterministic_output: fallback },
    schemaHint: 'CompanyResearchOutput',
    fallback,
    temperature: 0.2,
    topP: 1,
    maxTokens: 512,
  });
}

async function enhanceCommunicationSignal(input, fallback) {
  return generateSafeJson({
    moduleName: 'communication_signal',
    task: 'Produce professional communication signal JSON using only observable professional content in the input. Do not diagnose personality or infer private traits. Preserve the existing schema exactly.',
    input: { request: input, deterministic_output: fallback },
    schemaHint: 'PersonalityAnalysisOutput',
    fallback,
    temperature: 0.4,
    topP: 0.9,
    maxTokens: 2048,
  });
}

async function enhanceEmailWriting(input, fallback) {
  return generateSafeJson({
    moduleName: 'email_writing',
    task: 'Produce recruiter outreach email JSON using only final_personalization_payload. Keep subject under 8 words and body under 130 words. Do not invent facts or metrics. Preserve the existing schema exactly.',
    input: { request: input, deterministic_output: fallback },
    schemaHint: 'EmailPersonalizationOutput',
    fallback,
    temperature: 0.15,
    topP: 1,
    maxTokens: 2048,
  });
}

export async function supabaseHealth(_request, response, next) {
  try {
    const settings = getSupabaseSettings();
    const supabase = getSupabase();
    if (!supabase) {
      response.status(503).json({
        status: 'not_configured',
        supabaseConfigured: false,
        reason: 'SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set on Render.',
      });
      return;
    }

    const checks = {};
    checks.environment = {
      ok: settings.urlValid && settings.keyConfigured,
      host: settings.host,
      urlValid: settings.urlValid,
      serviceRoleKeyConfigured: settings.keyConfigured,
    };

    try {
      const restResponse = await fetchWithTimeout(`${settings.url}/rest/v1/`, {
        method: 'GET',
        headers: {
          apikey: process.env.SUPABASE_SERVICE_ROLE_KEY,
          Authorization: `Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}`,
        },
      });
      checks.supabase_rest_api = {
        ok: restResponse.status < 500,
        httpStatus: restResponse.status,
        reason: restResponse.statusText,
      };
    } catch (error) {
      checks.supabase_rest_api = {
        ok: false,
        ...safeErrorDetails(error),
      };
    }

    const candidateCheck = await supabase.from('candidate_assets_results').select('id').limit(1);
    checks.candidate_assets_results = candidateCheck.error
      ? { ok: false, ...safeErrorDetails(candidateCheck.error) }
      : { ok: true };

    const gmailCheck = await supabase.from('gmail_oauth_accounts').select('id').limit(1);
    checks.gmail_oauth_accounts = gmailCheck.error
      ? { ok: false, ...safeErrorDetails(gmailCheck.error) }
      : { ok: true };

    const emailCheck = await supabase.from('email_send_results').select('id').limit(1);
    checks.email_send_results = emailCheck.error
      ? { ok: false, ...safeErrorDetails(emailCheck.error) }
      : { ok: true };

    const campaignsCheck = await supabase.from('campaigns').select('id').limit(1);
    checks.campaigns = campaignsCheck.error
      ? { ok: false, ...safeErrorDetails(campaignsCheck.error) }
      : { ok: true };

    const campaignEmailsCheck = await supabase.from('campaign_emails').select('id').limit(1);
    checks.campaign_emails = campaignEmailsCheck.error
      ? { ok: false, ...safeErrorDetails(campaignEmailsCheck.error) }
      : { ok: true };

    const ok = Object.values(checks).every((check) => check.ok);
    response.status(ok ? 200 : 500).json({
      status: ok ? 'ok' : 'failed',
      supabaseConfigured: true,
      checks,
    });
  } catch (error) {
    next(supabaseWriteError('Supabase health check failed', error));
  }
}

export async function uploadSpreadsheet(request, response, next) {
  try {
    const user = await getAuthenticatedUser(request);
    const file = request.file;
    if (!file) {
      response.status(400).json({ error: 'No file uploaded.' });
      return;
    }

    const filename = file.originalname.replace(/[^\w.\- ]/g, '');
    const output = await runPython('parse-spreadsheet', {
      filename,
      content_base64: file.buffer.toString('base64'),
    });
    const supabase = getSupabase();
    let campaign = null;
    if (supabase) {
      const validRecipients = (output.rows || []).filter((row) => row.email && row.validation_status === 'valid');
      const totalEmails = validRecipients.length;
      const { data, error } = await supabase
        .from('campaigns')
        .insert({
          user_id: user.id,
          user_email: user.email,
          campaign_name: campaignNameFromFile(filename),
          file_name: filename,
          total_emails: totalEmails,
          sent_count: 0,
          failed_count: 0,
          pending_count: totalEmails,
          status: totalEmails > 0 ? CAMPAIGN_STATUSES.uploaded : CAMPAIGN_STATUSES.noRecipients,
          updated_at: new Date().toISOString(),
        })
        .select('*')
        .single();
      if (error) throw supabaseWriteError('Supabase campaign create failed', error);
      campaign = mapCampaign(data);

      if (validRecipients.length > 0) {
        const emailRecords = validRecipients.map((row) => ({
          campaign_id: campaign.id,
          user_id: user.id,
          user_email: user.email,
          recipient_email: row.email,
          recipient_name: row.name || '',
          company_name: row.company || '',
          status: 'Pending',
          row_data: row,
          updated_at: new Date().toISOString(),
        }));
        await assertSupabaseWrite(
          await supabase.from('campaign_emails').insert(emailRecords),
          'Supabase campaign email records create failed',
        );
      }
    }

    response.json({ ...output, campaign });
  } catch (error) {
    next(error);
  }
}

export async function listCampaigns(request, response, next) {
  try {
    const user = await getAuthenticatedUser(request);
    const supabase = getSupabase();
    if (!supabase) {
      response.json({ campaigns: [], summary: { totalCampaigns: 0, totalEmailsUploaded: 0, totalEmailsSent: 0, totalEmailsFailed: 0, totalEmailsPending: 0 } });
      return;
    }

    const { data, error } = await supabase
      .from('campaigns')
      .select('*')
      .eq('user_email', user.email)
      .order('created_at', { ascending: false });
    if (error) throw supabaseWriteError('Supabase campaigns fetch failed', error);

    const campaigns = (data || []).map(mapCampaign);
    const summary = campaigns.reduce((acc, campaign) => ({
      totalCampaigns: acc.totalCampaigns + 1,
      totalEmailsUploaded: acc.totalEmailsUploaded + campaign.totalEmails,
      totalEmailsSent: acc.totalEmailsSent + campaign.sentCount,
      totalEmailsFailed: acc.totalEmailsFailed + campaign.failedCount,
      totalEmailsPending: acc.totalEmailsPending + campaign.pendingCount,
    }), {
      totalCampaigns: 0,
      totalEmailsUploaded: 0,
      totalEmailsSent: 0,
      totalEmailsFailed: 0,
      totalEmailsPending: 0,
    });

    response.json({ campaigns, summary });
  } catch (error) {
    next(error);
  }
}

export async function getCampaign(request, response, next) {
  try {
    const user = await getAuthenticatedUser(request);
    const supabase = getSupabase();
    if (!supabase) {
      response.status(503).json({ error: 'Supabase is not configured.' });
      return;
    }

    const { data, error } = await supabase
      .from('campaigns')
      .select('*')
      .eq('id', request.params.id)
      .eq('user_email', user.email)
      .maybeSingle();
    if (error) throw supabaseWriteError('Supabase campaign fetch failed', error);
    if (!data) {
      response.status(404).json({ error: 'Campaign not found.' });
      return;
    }
    const emailsResult = await supabase
      .from('campaign_emails')
      .select('*')
      .eq('campaign_id', request.params.id)
      .eq('user_email', user.email)
      .order('created_at', { ascending: true });
    if (emailsResult.error) throw supabaseWriteError('Supabase campaign email fetch failed', emailsResult.error);
    response.json({ campaign: mapCampaign(data), emails: (emailsResult.data || []).map(mapCampaignEmail) });
  } catch (error) {
    next(error);
  }
}

export async function runCampaign(request, response, next) {
  try {
    const user = await getAuthenticatedUser(request);
    const campaignId = request.params.id;
    const supabase = getSupabase();
    if (!supabase) {
      response.status(503).json({ error: 'Supabase is not configured.' });
      return;
    }

    debugLog('Run campaign requested', { campaignId, userEmail: user.email });
    const campaignResult = await supabase
      .from('campaigns')
      .select('*')
      .eq('id', campaignId)
      .eq('user_email', user.email)
      .maybeSingle();
    if (campaignResult.error) throw supabaseWriteError('Supabase campaign ownership check failed', campaignResult.error);
    if (!campaignResult.data) {
      response.status(403).json({ error: 'Campaign not found or does not belong to the signed-in user.' });
      return;
    }

    const retryFailed = Boolean(request.body?.retryFailed);
    if (retryFailed) {
      await assertSupabaseWrite(await supabase
        .from('campaign_emails')
        .update({
          status: 'Pending',
          error_message: null,
          updated_at: new Date().toISOString(),
        })
        .eq('campaign_id', campaignId)
        .eq('user_email', user.email)
        .eq('status', 'Failed'), 'Supabase failed campaign email retry reset failed');
    }

    const pendingResult = await supabase
      .from('campaign_emails')
      .select('*')
      .eq('campaign_id', campaignId)
      .eq('user_email', user.email)
      .eq('status', 'Pending')
      .order('created_at', { ascending: true });
    if (pendingResult.error) throw supabaseWriteError('Supabase pending campaign emails fetch failed', pendingResult.error);

    const pendingEmails = pendingResult.data || [];
    debugLog('Pending campaign emails found', { campaignId, count: pendingEmails.length });
    if (pendingEmails.length === 0) {
      const campaign = await recalculateCampaignFromEmails({ campaignId, userEmail: user.email });
      response.json({ campaign, sentEmails: [], summary: { processed: 0, sent: 0, failed: 0, pending: campaign?.pendingCount || 0 }, message: 'No pending emails found for this campaign.' });
      return;
    }

    await recalculateCampaignFromEmails({ campaignId, userEmail: user.email, status: CAMPAIGN_STATUSES.processing });
    const candidate = await loadCandidateProfile(user.email);

    // Resolve which Gmail account to send from.
    // 1. Caller can pass gmail_address in the request body to pick a specific account.
    // 2. Otherwise load the most recently connected account from gmail_oauth_accounts.
    const requestedGmail = request.body?.gmail_address
      ? String(request.body.gmail_address).trim().toLowerCase()
      : null;

    const storedCredentials = requestedGmail
      ? await loadCredentialForAccount({ userId: user.id, userEmail: user.email, gmailAddress: requestedGmail })
      : await loadLatestCredential({ userId: user.id, userEmail: user.email });

    const gmailAddress = storedCredentials?.gmailAddress || user.email;
    const refreshToken = storedCredentials?.refreshToken;
    debugLog('OAuth2 configuration presence check', { campaignId, userEmail: user.email, gmailAddressPresent: Boolean(gmailAddress), refreshTokenPresent: Boolean(refreshToken) });

    if (!gmailAddress || !refreshToken) {
      const errorMessage = 'Email sending is not configured. Please connect your Gmail account via OAuth2 before running a campaign.';
      const campaign = await recalculateCampaignFromEmails({
        campaignId,
        userEmail: user.email,
        status: CAMPAIGN_STATUSES.uploaded,
      });
      response.status(400).json({ error: errorMessage, campaign, summary: { processed: 0, sent: 0, failed: 0, pending: pendingEmails.length } });
      return;
    }

    const directSendResults = [];
    let sent = 0;
    let failed = 0;

    for (const [index, record] of pendingEmails.entries()) {
      const row = record.row_data || {};
      const prospectId = `prospect-${index + 1}`;
      const targetRole = row.role || candidate.currentRole || 'Business Analyst';
      const targetCountry = row.country || candidate.preferredCountries || '';
      const companyName = row.company || record.company_name || '';
      const recipientEmail = record.recipient_email || row.email;

      let decisionOutput = {};
      let emailOutput = {};
      let sendOutput;
      try {
        const roleCountryInput = {
          campaign_id: campaignId,
          prospect_id: prospectId,
          target_role: targetRole,
          target_country: targetCountry,
          candidate_positioning: candidate.whyRelevant,
        };
        const roleCountryFallback = await runPython('role-country', roleCountryInput);
        const roleCountryOutput = await enhanceRoleCountry(roleCountryInput, roleCountryFallback);

        const linkedinInput = {
          full_name: row.name || record.recipient_name,
          role_title: targetRole,
          company_name: companyName,
          normalized_company_name: companyName,
          linkedin_url: row.linkedin_url || candidate.linkedInUrl || '',
          profile_summary: candidate.resumeSummary || '',
        };
        const linkedinFallback = await runPython('linkedin-research', linkedinInput);
        const linkedinOutput = await enhanceLinkedinResearch(linkedinInput, linkedinFallback);

        const companyInput = {
          campaign_id: campaignId,
          prospect_id: prospectId,
          company_name: companyName,
          company_website: row.company_website || row.website || '',
          target_role: targetRole,
          target_country: targetCountry,
          linkedin_research_status: linkedinOutput.research_status,
          approved_sources: [],
        };
        const companyFallback = await runPython('company-research', companyInput);
        const companyOutput = await enhanceCompanyResearch(companyInput, companyFallback);

        const personalityInput = {
          campaign_id: campaignId,
          prospect_id: prospectId,
          person_name: row.name || record.recipient_name,
          job_title: targetRole,
          company_name: companyName,
          linkedin_profile_summary: candidate.resumeSummary || '',
          company_research_summary: companyOutput.company_overview,
          role_country_intelligence: roleCountryOutput.email_positioning_angle,
        };
        const personalityFallback = await runPython('personality-analysis', personalityInput);
        const personalityOutput = await enhanceCommunicationSignal(personalityInput, personalityFallback);

        decisionOutput = await runPython('decision-engine', {
          campaign_id: campaignId,
          prospect_id: prospectId,
          cleaning_output: { ...row, full_name: row.name || record.recipient_name, role_title: targetRole, company_name: companyName },
          role_country_output: roleCountryOutput,
          linkedin_research_output: linkedinOutput,
          company_research_output: companyOutput,
          personality_analysis_output: personalityOutput,
          campaign_settings: {
            gmail_configured: true,
            gmail_valid: true,
            sending_enabled: true,
          },
        });
        const emailInput = {
          campaign_id: campaignId,
          prospect_id: prospectId,
          final_personalization_payload: decisionOutput.final_personalization_payload,
        };
        const emailFallback = await runPython('email-personalization', emailInput);
        emailOutput = await enhanceEmailWriting(emailInput, emailFallback);
        if (!emailIsSendable(decisionOutput, emailOutput)) {
          sendOutput = blockedSendResult(
            decisionOutput.email_send_block_reason
              || decisionOutput.decision_reason
              || emailOutput.email_generation_reason
              || 'Email was generated but did not pass direct-send safety gates.',
          );
        } else {
          sendOutput = await sendEmailWithRetry({
            gmailAddress,
            refreshToken,
            to: recipientEmail,
            subject: emailOutput.subject_line,
            body: emailOutput.email_body,
          });
        }
      } catch (error) {
        sendOutput = {
          send_status: 'send_failed',
          provider_message_id: '',
          send_reason: error.message || 'Email send failed.',
        };
      }

      const sentSuccessfully = sendOutput.send_status === 'sent';
      if (sentSuccessfully) sent += 1;
      else failed += 1;

      await assertSupabaseWrite(await supabase
        .from('campaign_emails')
        .update({
          subject: emailOutput.subject_line || '',
          email_body: emailOutput.email_body || '',
          status: sentSuccessfully ? 'Sent' : 'Failed',
          error_message: sentSuccessfully ? null : sendOutput.send_reason,
          sent_at: sentSuccessfully ? new Date().toISOString() : null,
          updated_at: new Date().toISOString(),
        })
        .eq('id', record.id)
        .eq('user_email', user.email), 'Supabase campaign email send result update failed');

      const resultPayload = {
        ...emailOutput,
        campaign_id: campaignId,
        prospect_id: prospectId,
        recipient_email: recipientEmail,
        send_status: sendOutput.send_status,
        send_reason: sendOutput.send_reason,
        provider_message_id: sendOutput.provider_message_id,
        sent_at: sentSuccessfully ? new Date().toISOString() : null,
      };
      directSendResults.push(resultPayload);
      await assertSupabaseWrite(await supabase.from('email_send_results').insert({
        campaign_id: campaignId,
        user_email: user.email,
        prospect_id: prospectId,
        recipient_email: recipientEmail,
        subject_line: emailOutput.subject_line || '',
        email_body: emailOutput.email_body || '',
        email_generation_status: emailOutput.email_generation_status || 'email_generation_failed',
        send_status: sendOutput.send_status,
        send_reason: sendOutput.send_reason,
        provider_message_id: sendOutput.provider_message_id,
        sent_at: resultPayload.sent_at,
        structured_output: resultPayload,
      }), 'Supabase sent email result save failed');

      debugLog('Campaign email send result', { campaignId, recipientEmail, status: sendOutput.send_status });
      await recalculateCampaignFromEmails({ campaignId, userEmail: user.email, status: CAMPAIGN_STATUSES.processing });
    }

    const campaign = await recalculateCampaignFromEmails({ campaignId, userEmail: user.email });
    debugLog('Campaign run finished', { campaignId, sent, failed, pending: campaign?.pendingCount || 0 });
    response.json({
      campaign,
      sentEmails: directSendResults,
      summary: { processed: pendingEmails.length, sent, failed, pending: campaign?.pendingCount || 0 },
    });
  } catch (error) {
    next(error);
  }
}

export async function validation(request, response) {
  response.json({ status: 'accepted', input: request.body });
}

export async function cleaning(request, response) {
  response.json({ status: 'accepted', input: request.body });
}

export async function roleCountry(request, response, next) {
  try {
    const fallback = await runPython('role-country', request.body);
    response.json(await enhanceRoleCountry(request.body, fallback));
  } catch (error) { next(error); }
}

export async function linkedinResearch(request, response, next) {
  try {
    const fallback = await runPython('linkedin-research', request.body);
    response.json(await enhanceLinkedinResearch(request.body, fallback));
  } catch (error) { next(error); }
}

export async function companyResearch(request, response, next) {
  try {
    const fallback = await runPython('company-research', request.body);
    response.json(await enhanceCompanyResearch(request.body, fallback));
  } catch (error) { next(error); }
}

export async function personalityAnalysis(request, response, next) {
  try {
    const fallback = await runPython('personality-analysis', request.body);
    response.json(await enhanceCommunicationSignal(request.body, fallback));
  } catch (error) { next(error); }
}

export async function candidateAssets(request, response, next) {
  try {
    const user = await getAuthenticatedUser(request);
    const body = request.body || {};
    const campaignId = body.campaign_id || 'campaign-demo';
    const candidateId = user.email;
    const payload = {
      campaign_id: campaignId,
      candidate_id: candidateId,
      linkedin_url: body.linkedInUrl || body.linkedin_url,
      youtube_video_url: body.youtubeUrl || body.youtube_video_url,
      resume_url: body.resumeUrl || '',
      portfolio_links: [body.githubUrl, body.portfolioUrl].filter(Boolean),
      candidate_positioning: body.whyRelevant || body.candidate_positioning,
      candidate_proof_points: [body.resumeSummary, body.skills].filter(Boolean),
      target_role: body.currentRole || 'Business Analyst',
    };
    const output = await runPython('candidate-assets', payload);

    const supabase = getSupabase();
    if (supabase) {
      await assertSupabaseWrite(await supabase
        .from('candidate_assets_results')
        .delete()
        .eq('campaign_id', campaignId)
        .eq('candidate_id', candidateId), 'Supabase candidate profile cleanup failed');

      await assertSupabaseWrite(await supabase.from('candidate_assets_results').insert({
        campaign_id: output.campaign_id || campaignId,
        candidate_id: output.candidate_id || candidateId,
        proof_status: output.proof_status || 'partial_proof_available',
        proof_reason: output.proof_reason || 'Candidate profile saved.',
        linkedin_profile_url: output.linkedin_profile_url || payload.linkedin_url || '',
        linkedin_profile_status: output.linkedin_profile_status || 'missing',
        resume_reference: output.resume_reference || {
          resume_available: Boolean(body.resumeFileName || body.resumeUrl),
          resume_type: body.resumeFileName ? 'uploaded_metadata' : '',
          resume_reference_url: body.resumeUrl || body.resumeFileName || '',
        },
        video_assets: output.video_assets || [],
        portfolio_assets: output.portfolio_assets || [],
        professional_positioning_summary: output.professional_positioning_summary || body.whyRelevant || 'Insufficient supporting proof.',
        why_relevant_summary: output.why_relevant_summary || body.whyRelevant || 'Insufficient supporting proof.',
        candidate_proof_snippets: output.candidate_proof_snippets || [body.skills, body.resumeSummary].filter(Boolean),
        asset_types_detected: output.asset_types_detected || [],
        manual_review_flag: Boolean(output.manual_review_flag),
        structured_output: {
          ...output,
          profile_form: {
            fullName: body.fullName || '',
            email: user.email,
            linkedInUrl: body.linkedInUrl || '',
            youtubeUrl: body.youtubeUrl || '',
            githubUrl: body.githubUrl || '',
            portfolioUrl: body.portfolioUrl || '',
            currentRole: body.currentRole || '',
            skills: body.skills || '',
            preferredCountries: body.preferredCountries || '',
            resumeSummary: body.resumeSummary || '',
            resumeFileName: body.resumeFileName || '',
            userId: user.id,
          },
        },
        updated_at: new Date().toISOString(),
      }), 'Supabase candidate profile save failed');
    }

    response.json({ ...output, candidate_profile_saved: Boolean(supabase), database_status: supabase ? 'saved' : 'not_configured' });
  } catch (error) {
    next(error);
  }
}

export async function candidateProfile(request, response, next) {
  try {
    const user = await getAuthenticatedUser(request);
    const email = user.email;

    const supabase = getSupabase();
    if (!supabase) {
      response.json({ profile: null, database_status: 'not_configured' });
      return;
    }

    const { data, error } = await supabase
      .from('candidate_assets_results')
      .select('structured_output, updated_at')
      .eq('candidate_id', email)
      .order('updated_at', { ascending: false })
      .limit(1)
      .maybeSingle();

    if (error) throw supabaseWriteError('Supabase candidate profile load failed', error);

    const gmailAccounts = await listGmailAccounts({ userId: user.id, userEmail: user.email });

    response.json({
      profile: data?.structured_output?.profile_form || null,
      updated_at: data?.updated_at || null,
      gmailAccounts,
    });
  } catch (error) {
    next(error);
  }
}

/**
 * GET /gmail-oauth-url
 * Returns the Google OAuth2 authorisation URL for the frontend to redirect to.
 */
export async function gmailOAuthUrl(request, response, next) {
  try {
    await getAuthenticatedUser(request);
    const clientId = process.env.GOOGLE_CLIENT_ID;
    if (!clientId) {
      response.status(503).json({ error: 'GOOGLE_CLIENT_ID is not configured on the server.' });
      return;
    }
    const redirectUri = process.env.GOOGLE_REDIRECT_URI
      || `${process.env.FRONTEND_ORIGIN || 'http://localhost:5173'}/gmail-callback`;

    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      response_type: 'code',
      scope: 'https://mail.google.com/',
      access_type: 'offline',
      prompt: 'consent select_account',
    });

    response.json({ url: `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}` });
  } catch (error) {
    next(error);
  }
}

/**
 * POST /gmail-auth
 * Receives the OAuth2 authorization code from the frontend, exchanges it for
 * tokens, and stores the encrypted refresh token in Supabase.
 */
export async function gmailAuth(request, response, next) {
  try {
    const user = await getAuthenticatedUser(request);
    const body = request.body || {};
    const campaignId = body.campaign_id || 'campaign-demo';
    const code = body.code;

    if (!code) {
      response.status(400).json({ error: 'OAuth2 authorization code is required.' });
      return;
    }

    const redirectUri = process.env.GOOGLE_REDIRECT_URI
      || `${process.env.FRONTEND_ORIGIN || 'http://localhost:5173'}/gmail-callback`;

    const { refreshToken, gmailAddress: tokenGmailAddress } = await exchangeCodeForTokens(code, redirectUri);

    // Use the Gmail address extracted from Google's id_token. Fall back to the
    // address the caller supplied, then to the signed-in user's email.
    const gmailAddress = tokenGmailAddress || body.gmailAddress || user.email;

    const stored = await saveGmailAccountCredential({
      userId: user.id,
      userEmail: user.email,
      gmailAddress,
      refreshToken,
    });

    response.json({
      gmail_address: stored.gmailAddress,
      gmail_status: 'connected',
      reason: 'Gmail connected via OAuth2. Refresh token stored securely.',
    });
  } catch (error) {
    next(error);
  }
}

export async function decisionEngine(request, response, next) {
  try { response.json(await runPython('decision-engine', request.body)); } catch (error) { next(error); }
}

export async function emailPersonalization(request, response, next) {
  try {
    const fallback = await runPython('email-personalization', request.body);
    response.json(await enhanceEmailWriting(request.body, fallback));
  } catch (error) { next(error); }
}

export async function runPipeline(request, response, next) {
  try {
    const user = await getAuthenticatedUser(request);
    const candidate = request.body.candidate || {};
    const rows = request.body.campaign?.upload?.rows || [];
    const campaignId = request.body.campaign?.upload?.campaign?.id || request.body.campaign?.id;
    if (!campaignId || rows.length === 0) {
      response.status(400).json({ error: 'Upload an Excel or CSV sheet to create a campaign before running the pipeline.' });
      return;
    }
    const candidateId = user.email;
    const directSendResults = [];
    const steps = [];
    let fallbacks = 0;
    let sent = 0;
    let failed = 0;

    const storedCredentials = await loadLatestCredential({ userId: user.id, userEmail: candidateId });
    const gmailAddress = storedCredentials?.gmailAddress || user.email;
    const refreshToken = storedCredentials?.refreshToken;
    const gmailReady = Boolean(gmailAddress && refreshToken);
    await updateCampaignCounts({
      campaignId,
      userEmail: user.email,
      totalEmails: rows.length,
      sentCount: 0,
      failedCount: 0,
      status: CAMPAIGN_STATUSES.processing,
    });

    for (const [index, row] of rows.entries()) {
      const prospectId = `prospect-${index + 1}`;
      const targetRole = row.role || row.Role || candidate.currentRole || 'Business Analyst';
      const targetCountry = row.country || row.Country || candidate.preferredCountries || '';
      const companyName = row.company || row.Company;
      const roleCountryOutput = await runPython('role-country', {
        campaign_id: campaignId,
        prospect_id: prospectId,
        target_role: targetRole,
        target_country: targetCountry,
        candidate_positioning: candidate.whyRelevant,
      });
      const linkedinOutput = await runPython('linkedin-research', {
        full_name: row.name || row.Name,
        role_title: targetRole,
        company_name: companyName,
        normalized_company_name: companyName,
        linkedin_url: row.linkedin_url || candidate.linkedInUrl || '',
        profile_summary: candidate.resumeSummary || '',
      });
      const companyOutput = await runPython('company-research', {
        campaign_id: campaignId,
        prospect_id: prospectId,
        company_name: companyName,
        company_website: row.company_website || row.website || '',
        target_role: targetRole,
        target_country: targetCountry,
        linkedin_research_status: linkedinOutput.research_status,
        approved_sources: [],
      });
      const personalityOutput = await runPython('personality-analysis', {
        campaign_id: campaignId,
        prospect_id: prospectId,
        person_name: row.name || row.Name,
        job_title: targetRole,
        company_name: companyName,
        linkedin_profile_summary: candidate.resumeSummary || '',
        company_research_summary: companyOutput.company_overview,
        role_country_intelligence: roleCountryOutput.email_positioning_angle,
      });
      const decisionOutput = await runPython('decision-engine', {
        campaign_id: campaignId,
        prospect_id: prospectId,
        cleaning_output: { ...row, full_name: row.name || row.Name, role_title: targetRole, company_name: companyName },
        role_country_output: roleCountryOutput,
        linkedin_research_output: linkedinOutput,
        company_research_output: companyOutput,
        personality_analysis_output: personalityOutput,
        campaign_settings: {
          oauth2_configured: Boolean(gmailAddress && refreshToken),
          oauth2_valid: Boolean(gmailAddress && refreshToken),
          sending_enabled: true,
        },
      });
      if (decisionOutput.fallback_used) fallbacks += 1;
      const emailOutput = await runPython('email-personalization', {
        campaign_id: campaignId,
        prospect_id: prospectId,
        final_personalization_payload: decisionOutput.final_personalization_payload,
      });

      const recipientEmail = row.email || row.Email;
      let sendOutput;
      if (!gmailReady) {
        sendOutput = blockedSendResult('Gmail is not connected. Connect your Gmail account via OAuth2 before running the pipeline.');
      } else if (!emailIsSendable(decisionOutput, emailOutput)) {
        sendOutput = blockedSendResult(
          decisionOutput.email_send_block_reason
            || decisionOutput.decision_reason
            || emailOutput.email_generation_reason
            || 'Email was generated but did not pass direct-send safety gates.',
        );
      } else {
        try {
          sendOutput = await sendEmailWithRetry({
            gmailAddress,
            refreshToken,
            to: recipientEmail,
            subject: emailOutput.subject_line,
            body: emailOutput.email_body,
          });
        } catch (error) {
          sendOutput = {
            send_status: 'send_failed',
            provider_message_id: '',
            send_reason: error.message || 'Email send failed.',
          };
        }
      }
      if (sendOutput.send_status === 'sent') sent += 1;
      else failed += 1;
      await updateCampaignCounts({
        campaignId,
        userEmail: user.email,
        totalEmails: rows.length,
        sentCount: sent,
        failedCount: failed,
        status: CAMPAIGN_STATUSES.processing,
      });

      directSendResults.push({
        ...emailOutput,
        campaign_id: campaignId,
        prospect_id: prospectId,
        decision_status: decisionOutput.decision_status,
        recipient_email: recipientEmail,
        send_status: sendOutput.send_status,
        send_reason: sendOutput.send_reason,
        provider_message_id: sendOutput.provider_message_id,
        sent_at: sendOutput.send_status === 'sent' ? new Date().toISOString() : null,
      });
    }

    ['Validation', 'Cleaning', 'Role-Country Intelligence', 'LinkedIn Research', 'Company Research', 'Communication Signals', 'Candidate Assets', 'Decision Engine', 'Email Generation', 'Gmail Send'].forEach((name) => {
      steps.push({ name, status: 'completed', reason: `${name} completed` });
    });

    const supabase = getSupabase();
    const campaign = await updateCampaignCounts({
      campaignId,
      userEmail: user.email,
      totalEmails: rows.length,
      sentCount: sent,
      failedCount: failed,
    });
    if (supabase) {
      await assertSupabaseWrite(await supabase.from('email_send_results').insert(directSendResults.map((result) => ({
        campaign_id: result.campaign_id,
        user_email: user.email,
        prospect_id: result.prospect_id,
        recipient_email: result.recipient_email,
        subject_line: result.subject_line,
        email_body: result.email_body,
        email_generation_status: result.email_generation_status,
        send_status: result.send_status,
        send_reason: result.send_reason,
        provider_message_id: result.provider_message_id,
        sent_at: result.sent_at,
        structured_output: result,
      }))), 'Supabase sent email save failed');
    }

    response.json({ steps, sentEmails: directSendResults, campaign, summary: { processed: rows.length, fallbacks, sent, failed, pending: Math.max(rows.length - sent - failed, 0) } });
  } catch (error) {
    next(error);
  }
}

// ---------------------------------------------------------------------------
// Gmail account management handlers (Phase 3)
// ---------------------------------------------------------------------------

/**
 * GET /gmail/accounts
 * Returns all active Gmail accounts connected by the signed-in user.
 */
export async function listGmailAccountsHandler(request, response, next) {
  try {
    const user = await getAuthenticatedUser(request);
    const accounts = await listGmailAccounts({ userId: user.id, userEmail: user.email });
    response.json({ gmailAccounts: accounts });
  } catch (error) {
    next(error);
  }
}

/**
 * DELETE /gmail/accounts/:gmailAddress
 * Revokes Google's token and soft-deletes the account record.
 */
export async function revokeGmailAccountHandler(request, response, next) {
  try {
    const user = await getAuthenticatedUser(request);
    const gmailAddress = decodeURIComponent(request.params.gmailAddress || '').trim().toLowerCase();
    if (!gmailAddress) {
      response.status(400).json({ error: 'gmailAddress is required.' });
      return;
    }
    const result = await revokeGmailAccount({ userId: user.id, userEmail: user.email, gmailAddress });
    response.json(result);
  } catch (error) {
    next(error);
  }
}
