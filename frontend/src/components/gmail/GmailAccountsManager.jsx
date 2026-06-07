import { useState } from 'react';
import { toast } from 'react-toastify';
import { CheckCircle2, Mail, Trash2, Plus, Loader2 } from 'lucide-react';
import { getJson, deleteJson } from '../../services/api.js';
import Button from '../ui/Button.jsx';

/**
 * Displays the list of connected Gmail accounts and lets the user
 * add new ones or disconnect existing ones.
 *
 * Props:
 *   accounts       – array of { gmailAddress, connectedAt } from the parent
 *   onAccountsChange – callback(newAccountsArray) so the parent stays in sync
 *   campaignId     – stashed in sessionStorage before the OAuth redirect
 */
export default function GmailAccountsManager({ accounts = [], onAccountsChange = () => {}, campaignId }) {
  const [disconnecting, setDisconnecting] = useState('');
  const [confirmTarget, setConfirmTarget] = useState('');

  async function connectGmail() {
    try {
      sessionStorage.setItem('gmail_oauth_campaign_id', campaignId || 'campaign-demo');
      const { url } = await getJson('/gmail-oauth-url');
      window.location.href = url;
    } catch (error) {
      toast.error(error?.response?.data?.error || 'Could not start Gmail OAuth flow.');
    }
  }

  function askConfirm(gmailAddress) {
    setConfirmTarget(gmailAddress);
  }

  function cancelConfirm() {
    setConfirmTarget('');
  }

  async function disconnect(gmailAddress) {
    setDisconnecting(gmailAddress);
    setConfirmTarget('');
    try {
      await deleteJson(`/gmail/accounts/${encodeURIComponent(gmailAddress)}`);
      toast.success(`${gmailAddress} disconnected.`);
      const updated = accounts.filter((a) => a.gmailAddress !== gmailAddress);
      onAccountsChange(updated);
    } catch (error) {
      toast.error(error?.response?.data?.error || 'Could not disconnect Gmail account.');
    } finally {
      setDisconnecting('');
    }
  }

  return (
    <div className="space-y-3">
      <span className="text-sm font-medium text-slate-700">Gmail — Sending Accounts</span>

      {accounts.length === 0 && (
        <p className="text-sm text-slate-400">No Gmail accounts connected yet.</p>
      )}

      <ul className="space-y-2">
        {accounts.map(({ gmailAddress, connectedAt }) => (
          <li
            key={gmailAddress}
            className="flex items-center justify-between gap-3 rounded-lg border border-green-200 bg-green-50 px-4 py-2"
          >
            <div className="flex items-center gap-2 text-sm text-green-700">
              <CheckCircle2 size={15} />
              <span className="font-medium">{gmailAddress}</span>
              {connectedAt && (
                <span className="text-xs text-green-500">
                  connected {new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(connectedAt))}
                </span>
              )}
            </div>

            {confirmTarget === gmailAddress ? (
              <div className="flex items-center gap-2">
                <span className="text-xs text-red-600">Remove this account?</span>
                <button
                  type="button"
                  onClick={() => disconnect(gmailAddress)}
                  className="rounded bg-red-600 px-2 py-1 text-xs text-white hover:bg-red-700"
                >
                  Yes, remove
                </button>
                <button
                  type="button"
                  onClick={cancelConfirm}
                  className="rounded border border-slate-300 px-2 py-1 text-xs text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => askConfirm(gmailAddress)}
                disabled={disconnecting === gmailAddress}
                className="flex items-center gap-1 rounded p-1 text-slate-400 hover:text-red-500 disabled:opacity-50"
                title="Disconnect this Gmail account"
              >
                {disconnecting === gmailAddress
                  ? <Loader2 size={15} className="animate-spin" />
                  : <Trash2 size={15} />}
              </button>
            )}
          </li>
        ))}
      </ul>

      <Button type="button" variant="secondary" onClick={connectGmail}>
        <Plus size={15} />
        {accounts.length === 0 ? 'Connect Gmail' : 'Add another Gmail account'}
      </Button>

      <p className="text-xs text-slate-400">
        Authorises Kiro to send emails on your behalf via OAuth2. No password stored.
      </p>
    </div>
  );
}
