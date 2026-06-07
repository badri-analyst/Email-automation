import { useEffect, useMemo } from 'react';
import { toast } from 'react-toastify';
import { getJson, postJson } from '../services/api.js';
import { useAsyncAction } from '../hooks/useAsyncAction.js';
import { useOutreach } from '../context/OutreachContext.jsx';
import Button from '../components/ui/Button.jsx';
import Card from '../components/ui/Card.jsx';
import PipelineStepper from '../components/pipeline/PipelineStepper.jsx';
import ProcessingLogs from '../components/pipeline/ProcessingLogs.jsx';

const CAMPAIGN_RUN_TIMEOUT_MS = 30 * 60 * 1000;

export default function PipelineExecution() {
  const { state, dispatch } = useOutreach();
  const { loading, run } = useAsyncAction();
  const activeCampaign = useMemo(() => {
    const campaigns = state.campaigns || [];
    const selectedId = state.campaign?.upload?.campaign?.id || state.campaign?.id;
    const selected = campaigns.find((campaign) => campaign.id === selectedId && campaign.pendingCount > 0);
    return selected
      || campaigns.find((campaign) => campaign.pendingCount > 0)
      || campaigns.find((campaign) => campaign.failedCount > 0)
      || campaigns[0]
      || null;
  }, [state.campaign?.id, state.campaign?.upload?.campaign?.id, state.campaigns]);

  async function loadCampaigns() {
    const data = await getJson('/campaigns');
    dispatch({ type: 'SET_CAMPAIGNS', payload: data });
    return data.campaigns || [];
  }

  useEffect(() => {
    loadCampaigns().catch((error) => {
      toast.error(error?.response?.data?.error || 'Could not load campaigns.');
    });
  }, []);

  async function runPipeline() {
    const campaigns = state.campaigns?.length ? state.campaigns : await loadCampaigns();
    const selectedId = state.campaign?.upload?.campaign?.id || state.campaign?.id;
    const selected = campaigns.find((campaign) => campaign.id === selectedId && campaign.pendingCount > 0)
      || campaigns.find((campaign) => campaign.pendingCount > 0)
      || campaigns.find((campaign) => campaign.failedCount > 0);
    if (!selected?.id) {
      toast.error('Upload an Excel sheet to create a campaign before running.');
      return;
    }
    const retryFailed = selected.pendingCount === 0 && selected.failedCount > 0;
    if (selected.pendingCount === 0 && !retryFailed) {
      toast.info('This campaign has no pending emails to send.');
      return;
    }
    const data = await run(
      () => postJson(`/campaigns/${selected.id}/run`, { retryFailed }, { timeout: CAMPAIGN_RUN_TIMEOUT_MS }),
      { success: retryFailed ? 'Failed emails queued and campaign rerun completed' : 'Campaign run completed' },
    );
    dispatch({ type: 'SET_PIPELINE', payload: data.steps || [] });
    dispatch({ type: 'SET_SENT_EMAILS', payload: data.sentEmails || [] });
    dispatch({ type: 'SET_RESULTS', payload: data.summary || {} });
    if (data.campaign) {
      dispatch({ type: 'SET_CURRENT_CAMPAIGN', payload: { id: data.campaign.id, name: data.campaign.campaignName } });
    }
    await loadCampaigns();
    if ((data.summary?.failed || 0) > 0) {
      toast.warning(`${data.summary.failed} email(s) failed. Open Results to see the reason.`);
    } else if ((data.summary?.sent || 0) > 0) {
      toast.success(`${data.summary.sent} email(s) sent.`);
    } else if (data.message) {
      toast.info(data.message);
    } else {
      toast.info('Pipeline finished without sent emails.');
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h2 className="text-3xl font-bold text-slate-950">Pipeline execution</h2>
          <p className="mt-2 text-slate-500">
            {activeCampaign
              ? `Selected campaign: ${activeCampaign.campaignName} (${activeCampaign.pendingCount} pending, ${activeCampaign.failedCount} failed).`
              : 'Upload a campaign sheet before running.'}
          </p>
        </div>
        <Button onClick={runPipeline} disabled={loading}>{loading ? 'Running campaign...' : 'Run Campaign'}</Button>
      </div>
      <PipelineStepper steps={state.pipeline} />
      <div className="grid gap-4 lg:grid-cols-4">
        <Card><h3 className="font-semibold">Rows processed</h3><p className="mt-2 text-3xl font-bold">{state.results.processed || 0}</p></Card>
        <Card><h3 className="font-semibold">Fallbacks used</h3><p className="mt-2 text-3xl font-bold">{state.results.fallbacks || 0}</p></Card>
        <Card><h3 className="font-semibold">Emails sent</h3><p className="mt-2 text-3xl font-bold">{state.results.sent || 0}</p></Card>
        <Card><h3 className="font-semibold">Emails failed</h3><p className="mt-2 text-3xl font-bold">{state.results.failed || 0}</p></Card>
      </div>
      <ProcessingLogs logs={state.pipeline.map((step) => ({ stage: step.name, status: step.status, message: step.reason }))} />
    </div>
  );
}
