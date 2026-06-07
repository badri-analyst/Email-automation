import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { postJson } from '../services/api.js';
import Loader from '../components/ui/Loader.jsx';

/**
 * Landing page for the Google OAuth2 redirect.
 * Google returns to /gmail-callback?code=...
 * We exchange the code for tokens via the backend, then redirect back to
 * /candidate where GmailAccountsManager will reload and show the new account.
 */
export default function GmailCallback() {
  const navigate = useNavigate();
  const ran = useRef(false);

  useEffect(() => {
    if (ran.current) return;
    ran.current = true;

    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    const error = params.get('error');

    if (error) {
      toast.error(`Gmail authorisation was denied: ${error}`);
      navigate('/candidate', { replace: true });
      return;
    }

    if (!code) {
      toast.error('No authorisation code received from Google.');
      navigate('/candidate', { replace: true });
      return;
    }

    const campaignId = sessionStorage.getItem('gmail_oauth_campaign_id') || 'campaign-demo';
    sessionStorage.removeItem('gmail_oauth_campaign_id');

    // Signal to /candidate that it should refresh the Gmail accounts list.
    sessionStorage.setItem('gmail_just_connected', '1');

    postJson('/gmail-auth', { code, campaign_id: campaignId })
      .then((result) => {
        toast.success(result.reason || 'Gmail connected successfully.');
      })
      .catch((err) => {
        sessionStorage.removeItem('gmail_just_connected');
        const status = err?.response?.status;
        if (status === 401) {
          toast.error('Your session expired. Please sign in again and reconnect Gmail.');
        } else {
          toast.error(err?.response?.data?.error || 'Gmail OAuth connection failed.');
        }
      })
      .finally(() => {
        navigate('/candidate', { replace: true });
      });
  }, []);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="flex flex-col items-center gap-4 text-slate-600">
        <Loader />
        <p className="text-sm">Connecting your Gmail account…</p>
      </div>
    </div>
  );
}
