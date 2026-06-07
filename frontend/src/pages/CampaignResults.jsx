import { useEffect, useMemo, useState } from 'react';
import { toast } from 'react-toastify';
import Card from '../components/ui/Card.jsx';
import Button from '../components/ui/Button.jsx';
import CampaignResultsTable from '../components/tables/CampaignResultsTable.jsx';
import { useOutreach } from '../context/OutreachContext.jsx';
import { getJson } from '../services/api.js';

export default function CampaignResults() {
  const { state, dispatch } = useOutreach();
  const [campaignEmails, setCampaignEmails] = useState([]);
  const [loading, setLoading] = useState(false);
  const selectedCampaign = useMemo(() => {
    const campaigns = state.campaigns || [];
    const selectedId = state.campaign?.upload?.campaign?.id || state.campaign?.id;
    return campaigns.find((campaign) => campaign.id === selectedId)
      || campaigns[0]
      || null;
  }, [state.campaign?.id, state.campaign?.upload?.campaign?.id, state.campaigns]);

  async function loadResults() {
    setLoading(true);
    try {
      const campaignData = await getJson('/campaigns');
      dispatch({ type: 'SET_CAMPAIGNS', payload: campaignData });
      const campaigns = campaignData.campaigns || [];
      const currentId = selectedCampaign?.id || campaigns[0]?.id;
      if (!currentId) {
        setCampaignEmails([]);
        return;
      }
      const detail = await getJson(`/campaigns/${currentId}`);
      setCampaignEmails(detail.emails || []);
    } catch (error) {
      toast.error(error?.response?.data?.error || 'Could not load campaign results.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadResults();
  }, []);

  const rows = (campaignEmails.length ? campaignEmails : state.sentEmails).map((email, index) => ({
    prospect_id: email.prospect_id || `row-${index + 1}`,
    recipient_email: email.recipientEmail || email.recipient_email,
    decision_status: email.decision_status || '-',
    email_generation_status: email.email_generation_status || (email.subject ? 'email_ready' : '-'),
    send_status: email.send_status || email.status,
    send_reason: email.send_reason || email.errorMessage || '-',
  }));

  function downloadCsv() {
    const headers = ['prospect_id', 'recipient_email', 'decision_status', 'email_generation_status', 'send_status', 'send_reason'];
    const csv = [headers.join(','), ...rows.map((row) => headers.map((h) => JSON.stringify(row[h] ?? '')).join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'campaign-results.csv';
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div><h2 className="text-3xl font-bold text-slate-950">Campaign results</h2><p className="mt-2 text-slate-500">Inspect sent emails, failed sends, and export campaign status.</p></div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={loadResults} disabled={loading}>{loading ? 'Refreshing...' : 'Refresh'}</Button>
          <Button variant="secondary" onClick={downloadCsv}>Download CSV</Button>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-4">
        <Card><p className="text-sm text-slate-500">Sent emails</p><p className="mt-2 text-2xl font-bold">{rows.filter((d) => ['sent', 'Sent'].includes(d.send_status)).length}</p></Card>
        <Card><p className="text-sm text-slate-500">Pending emails</p><p className="mt-2 text-2xl font-bold">{rows.filter((d) => d.send_status === 'Pending').length}</p></Card>
        <Card><p className="text-sm text-slate-500">Total rows</p><p className="mt-2 text-2xl font-bold">{rows.length}</p></Card>
        <Card><p className="text-sm text-slate-500">Failed emails</p><p className="mt-2 text-2xl font-bold">{rows.filter((d) => ['send_failed', 'Failed'].includes(d.send_status)).length}</p></Card>
      </div>
      <CampaignResultsTable rows={rows} />
    </div>
  );
}
