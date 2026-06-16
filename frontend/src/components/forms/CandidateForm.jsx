import { useEffect, useRef, useState } from 'react';
import { toast } from 'react-toastify';
import { useAuth } from '../../context/AuthContext.jsx';
import { getJson, postJson, uploadFile } from '../../services/api.js';
import { useAsyncAction } from '../../hooks/useAsyncAction.js';
import { useOutreach } from '../../context/OutreachContext.jsx';
import { isEmail, isLinkedInProfile, isYouTube, sanitizeText } from '../../utils/validators.js';
import Button from '../ui/Button.jsx';
import FileDropzone from '../upload/FileDropzone.jsx';
import GmailAccountsManager from '../gmail/GmailAccountsManager.jsx';


const initial = {
  fullName: '',
  email: '',
  phone: '',
  linkedInUrl: '',
  youtubeUrl: '',
  whyRelevant: '',
  githubUrl: '',
  portfolioUrl: '',
  resumeUrl: '',
  currentRole: '',
  targetRole: '',
  skills: '',
  preferredCountries: '',
  resumeSummary: '',
  companyResearchApiKey: '',
  companyResearchBackupKey: '',
  companyResearchBaseUrl: '',
  companyResearchModel: '',
  emailWritingApiKey: '',
  emailWritingBackupKey: '',
  emailWritingBaseUrl: '',
  emailWritingModel: '',
};

export default function CandidateForm({ highlightGmail = false }) {
  const { state, dispatch } = useOutreach();
  const { user } = useAuth();
  const gmailRef = useRef(null);
  const [form, setForm] = useState({ ...initial, ...state.candidate });
  const [resume, setResume] = useState(null);
  const [resumeUploaded, setResumeUploaded] = useState(false);
  const [gmailAccounts, setGmailAccounts] = useState([]);
  const { loading, run } = useAsyncAction();

  useEffect(() => {
    if (!user?.email) {
      setForm(initial);
      setGmailAccounts([]);
      dispatch({ type: 'SET_CANDIDATE', payload: {} });
      return undefined;
    }

    let cancelled = false;
    async function loadProfile() {
      try {
        const data = await getJson('/candidate-profile');
        const profile = data.profile || {};
        const next = {
          ...initial,
          ...profile,
          fullName: profile.fullName || user.name || '',
          email: user.email,
        };
        if (cancelled) return;
        setForm(next);
        setGmailAccounts(data.gmailAccounts || []);
        dispatch({ type: 'SET_CANDIDATE', payload: next });
      } catch (error) {
        toast.error(error?.response?.data?.error || 'Could not load saved candidate profile.');
      }
    }

    loadProfile();
    return () => {
      cancelled = true;
    };
  }, [user?.email]);

  // Scroll to Gmail section if user arrived from pipeline Gmail error
  useEffect(() => {
    if (highlightGmail && gmailRef.current) {
      setTimeout(() => gmailRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' }), 400);
    }
  }, [highlightGmail]);

  // After returning from the Gmail OAuth redirect, reload the accounts list.
  useEffect(() => {
    if (!sessionStorage.getItem('gmail_just_connected')) return;
    sessionStorage.removeItem('gmail_just_connected');
    getJson('/gmail/accounts')
      .then((data) => setGmailAccounts(data.gmailAccounts || []))
      .catch(() => {});
  }, []);

  function update(key, value) {
    const next = { ...form, [key]: value };
    setForm(next);
    dispatch({ type: 'SET_CANDIDATE', payload: next });
  }

  function validate() {
    const email = String(user?.email || form.email || '').trim().toLowerCase();
    if (form.fullName.trim().length < 2) return 'Name must be at least 2 characters.';
    if (!isEmail(email)) return 'Enter a valid email address.';
    if (!isLinkedInProfile(form.linkedInUrl)) return 'LinkedIn URL must be a linkedin.com/in/ profile.';
    if (!isYouTube(form.youtubeUrl)) return 'Enter a valid YouTube URL or leave it blank.';
    if (form.whyRelevant.length > 900) return 'Why relevant summary must stay under 900 characters.';
    return '';
  }

  async function submit(event) {
    event.preventDefault();
    const error = validate();
    if (error) {
      toast.error(error);
      return;
    }
    const payload = Object.fromEntries(Object.entries(form).map(([key, value]) => [key, sanitizeText(value)]));
    payload.email = String(user?.email || payload.email || '').trim().toLowerCase();
    payload.fullName = payload.fullName || user?.name || '';
    payload.resumeFileName = resume?.name || '';
    await run(async () => {
      // Upload resume file first if a new one was selected
      if (resume && !resumeUploaded) {
        await uploadFile('/resume/upload', resume, {}, null);
        setResumeUploaded(true);
        toast.info('Resume uploaded — will be attached to every email.');
      }
      const candidateAssets = await postJson('/candidate-assets', {
        ...payload,
        campaign_id: state.campaign.id,
        candidate_id: payload.email,
      });
      toast.success('Candidate profile saved.');
      return candidateAssets;
    });
  }

  return (
    <form className="grid gap-5 lg:grid-cols-2" onSubmit={submit}>
      {[
        ['fullName', 'Full Name', 'text'],
        ['email', 'Email Address', 'email'],
        ['phone', 'Phone Number', 'tel'],
        ['linkedInUrl', 'LinkedIn URL', 'url'],
        ['youtubeUrl', 'YouTube Video Link', 'url'],
        ['githubUrl', 'GitHub URL', 'url'],
        ['portfolioUrl', 'Portfolio URL', 'url'],
        ['resumeUrl', 'Resume Link (Google Drive / Dropbox)', 'url'],
        ['currentRole', 'Current Role', 'text'],
        ['targetRole', 'Role You Are Targeting (e.g. SAP Basis Consultant)', 'text'],
        ['skills', 'Skills', 'text'],
        ['preferredCountries', 'Preferred Countries', 'text'],
      ].map(([key, label, type]) => (
        <label key={key} className="block">
          <span className="text-sm font-medium text-slate-700">{label}</span>
          <input
            type={type}
            value={key === 'email' && user?.email ? user.email : (form[key] || '')}
            onChange={(event) => update(key, event.target.value)}
            readOnly={key === 'email' && Boolean(user?.email)}
            className={`focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm ${key === 'email' && user?.email ? 'bg-slate-50 text-slate-500' : 'bg-white'}`}
          />
        </label>
      ))}

      {/* Gmail OAuth2 multi-account manager */}
      <div ref={gmailRef} className={`block lg:col-span-2 rounded-xl transition-all duration-500 ${highlightGmail ? 'ring-2 ring-amber-400 ring-offset-2 p-3' : ''}`}>
        <GmailAccountsManager
          accounts={gmailAccounts}
          onAccountsChange={setGmailAccounts}
          campaignId={state.campaign?.id}
        />
      </div>

      {/* API Keys Section */}
      <div className="lg:col-span-2 rounded-xl border border-slate-200 bg-slate-50 p-4">
        <p className="mb-1 text-sm font-semibold text-slate-700">AI API Keys</p>
        <p className="mb-4 text-xs text-slate-500">
          Works with any provider — NVIDIA, Gemini, OpenAI, Groq, Mistral, Together AI, or any OpenAI-compatible API.
          Leave Base URL and Model blank to use defaults (NVIDIA NIM).
        </p>

        <p className="mb-2 text-xs font-semibold text-slate-600 uppercase tracking-wide">Company Research</p>
        <div className="grid gap-3 lg:grid-cols-2 mb-4">
          {[
            ['companyResearchApiKey', 'Primary API Key', 'password', 'Your API key'],
            ['companyResearchBackupKey', 'Backup API Key', 'password', 'Backup key (optional)'],
            ['companyResearchBaseUrl', 'Base URL (optional)', 'url', 'https://integrate.api.nvidia.com/v1'],
            ['companyResearchModel', 'Model (optional)', 'text', 'meta/llama-4-maverick-17b-128e-instruct'],
          ].map(([key, label, type, placeholder]) => (
            <label key={key} className="block">
              <span className="text-sm font-medium text-slate-700">{label}</span>
              <input
                type={type}
                value={form[key] || ''}
                onChange={(event) => update(key, event.target.value)}
                placeholder={placeholder}
                className="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm bg-white font-mono"
              />
            </label>
          ))}
        </div>

        <p className="mb-2 text-xs font-semibold text-slate-600 uppercase tracking-wide">Email Writing</p>
        <div className="grid gap-3 lg:grid-cols-2">
          {[
            ['emailWritingApiKey', 'Primary API Key', 'password', 'Your API key'],
            ['emailWritingBackupKey', 'Backup API Key', 'password', 'Backup key (optional)'],
            ['emailWritingBaseUrl', 'Base URL (optional)', 'url', 'https://integrate.api.nvidia.com/v1'],
            ['emailWritingModel', 'Model (optional)', 'text', 'mistralai/mistral-large-3-675b-instruct-2512'],
          ].map(([key, label, type, placeholder]) => (
            <label key={key} className="block">
              <span className="text-sm font-medium text-slate-700">{label}</span>
              <input
                type={type}
                value={form[key] || ''}
                onChange={(event) => update(key, event.target.value)}
                placeholder={placeholder}
                className="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm bg-white font-mono"
              />
            </label>
          ))}
        </div>
      </div>

      <label className="block lg:col-span-2">
        <span className="text-sm font-medium text-slate-700">Why I May Be Relevant</span>
        <textarea
          value={form.whyRelevant}
          maxLength={900}
          onChange={(event) => update('whyRelevant', event.target.value)}
          className="focus-ring mt-1 min-h-28 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
          placeholder="Keep this factual: workflow clarity, stakeholder alignment, delivery coordination..."
        />
      </label>
      <label className="block lg:col-span-2">
        <span className="text-sm font-medium text-slate-700">Resume Summary</span>
        <textarea
          value={form.resumeSummary}
          onChange={(event) => update('resumeSummary', event.target.value)}
          className="focus-ring mt-1 min-h-24 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
        />
      </label>
      <div className="lg:col-span-2">
        <FileDropzone
          accept={{ 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] }}
          onFile={(file) => { setResume(file); setResumeUploaded(false); }}
          label={resumeUploaded ? `✓ Resume attached: ${resume?.name}` : resume ? resume.name : 'Upload resume PDF/DOCX — will be attached to every email sent'}
        />
        {resumeUploaded && (
          <p className="mt-1 text-xs text-emerald-600">Resume will be attached to every outreach email.</p>
        )}
      </div>
      <div className="lg:col-span-2">
        <Button disabled={loading}>{loading ? 'Saving...' : 'Save candidate profile'}</Button>
      </div>
    </form>
  );
}
