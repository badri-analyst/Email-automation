import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FileUp, Mail } from 'lucide-react';
import { getJson } from '../services/api.js';
import { useAsyncAction } from '../hooks/useAsyncAction.js';
import { useOutreach } from '../context/OutreachContext.jsx';
import Button from '../components/ui/Button.jsx';
import Card from '../components/ui/Card.jsx';
import StatusBadge from '../components/ui/StatusBadge.jsx';


function SummaryCard({ label, value }) {
  return (
    <Card>
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-bold text-slate-950">{value || 0}</p>
    </Card>
  );
}

function formatDate(value) {
  if (!value) return '-';
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value));
}

export default function Campaigns() {
  const { state, dispatch } = useOutreach();
  const { loading, run } = useAsyncAction();
  const [gmailAccounts, setGmailAccounts] = useState([]);
  const navigate = useNavigate();
  const summary = state.campaignSummary || {};

  async function loadCampaigns() {
    const data = await run(() => getJson('/campaigns'));
    dispatch({ type: 'SET_CAMPAIGNS', payload: data });
  }

  useEffect(() => {
    loadCampaigns();
    getJson('/gmail/accounts')
      .then((data) => {
        const accounts = data.gmailAccounts || [];
        setGmailAccounts(accounts);
      })
      .catch(() => { toast.warn('Could not load connected Gmail accounts.'); });
  }, []);

  function startNewCampaign() {
    dispatch({ type: 'RESET_CAMPAIGN_FLOW' });
    navigate('/upload');
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h2 className="text-3xl font-bold text-slate-950">Campaigns</h2>
          <p className="mt-2 text-slate-500">Track uploaded sheets and email sending progress for your account.</p>
        </div>
        <div className="flex items-center gap-3">
          {gmailAccounts.length > 0 && (
            <div className="flex items-center gap-1.5 text-sm text-slate-500">
              <Mail size={14} className="text-green-500" />
              {gmailAccounts[0].gmailAddress}
            </div>
          )}
          <Button onClick={startNewCampaign}><FileUp size={16} /> New campaign</Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-5">
        <SummaryCard label="Total Campaigns" value={summary.totalCampaigns} />
        <SummaryCard label="Emails Uploaded" value={summary.totalEmailsUploaded} />
        <SummaryCard label="Emails Sent" value={summary.totalEmailsSent} />
        <SummaryCard label="Emails Failed" value={summary.totalEmailsFailed} />
        <SummaryCard label="Emails Pending" value={summary.totalEmailsPending} />
      </div>

      <div className="overflow-auto rounded-xl border border-slate-200 bg-white">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
            <tr>
              {['Campaign Name', 'File Name', 'Total Emails', 'Sent', 'Failed', 'Pending', 'Status', 'Created Date'].map((header) => (
                <th key={header} className="px-4 py-3">{header}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {state.campaigns.map((campaign) => (
              <tr key={campaign.id}>
                <td className="px-4 py-3 font-medium text-slate-900">{campaign.campaignName}</td>
                <td className="max-w-72 truncate px-4 py-3" title={campaign.fileName}>{campaign.fileName}</td>
                <td className="px-4 py-3">{campaign.totalEmails}</td>
                <td className="px-4 py-3 font-medium text-emerald-700">{campaign.sentCount}</td>
                <td className="px-4 py-3 font-medium text-rose-600">{campaign.failedCount}</td>
                <td className="px-4 py-3">{campaign.pendingCount}</td>
                <td className="px-4 py-3"><StatusBadge status={campaign.status}>{campaign.status}</StatusBadge></td>
                <td className="px-4 py-3">{formatDate(campaign.createdAt)}</td>
              </tr>
            ))}
            {!loading && state.campaigns.length === 0 && (
              <tr>
                <td className="px-4 py-6 text-center text-slate-500" colSpan={8}>No campaigns yet. Upload an Excel sheet to create one.</td>
              </tr>
            )}
            {loading && (
              <tr>
                <td className="px-4 py-6 text-center text-slate-500" colSpan={8}>Loading campaigns...</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
