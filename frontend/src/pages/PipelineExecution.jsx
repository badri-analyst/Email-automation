import { useEffect, useRef, useState } from 'react';
import { toast } from 'react-toastify';
import { getJson, postJson } from '../services/api.js';
import { useOutreach } from '../context/OutreachContext.jsx';
import Card from '../components/ui/Card.jsx';
import StatusBadge from '../components/ui/StatusBadge.jsx';

const CAMPAIGN_RUN_TIMEOUT_MS = 30 * 60 * 1000;

const STEP_NAMES = [
  'Validation',
  'Cleaning',
  'Role-Country Intelligence',
  'LinkedIn Research',
  'Company Research',
  'Communication Signals',
  'Candidate Assets',
  'Decision Engine',
  'Email Generation',
  'Gmail Send',
];

// Approximate time each step takes (ms) — used for animated progress only
const STEP_DURATIONS = [800, 800, 2000, 3000, 2500, 2000, 1500, 1500, 3000, 2000];

function StepCard({ name, index, status, reason, processed, total }) {
  const isActive = status === 'active';
  const isDone = status === 'completed';
  const isFailed = status === 'failed';

  const border = isActive
    ? 'border-blue-300 shadow-blue-100'
    : isDone
    ? 'border-emerald-200'
    : isFailed
    ? 'border-rose-200'
    : 'border-slate-200';

  return (
    <div className={`rounded-xl border bg-white p-4 shadow-sm transition ${border}`}>
      <div className="mb-3 flex items-center justify-between">
        <span className="grid h-8 w-8 place-items-center rounded-full bg-slate-100 text-sm font-semibold text-slate-600">
          {index + 1}
        </span>
        <StatusBadge status={isActive ? 'active' : status}>{isActive ? 'processing' : status}</StatusBadge>
      </div>
      <p className="text-sm font-semibold text-slate-900">{name}</p>
      {isActive && total > 0 && (
        <div className="mt-2">
          <div className="mb-1 flex justify-between text-xs text-slate-500">
            <span>Processing…</span>
            <span>{processed}/{total}</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-blue-500 transition-all duration-500"
              style={{ width: total > 0 ? `${Math.round((processed / total) * 100)}%` : '0%' }}
            />
          </div>
        </div>
      )}
      {!isActive && (
        <p className="mt-1 text-xs text-slate-500">{reason || 'Waiting for input'}</p>
      )}
    </div>
  );
}

export default function PipelineExecution() {
  const { state, dispatch } = useOutreach();
  const [stepStatuses, setStepStatuses] = useState(
    STEP_NAMES.map(() => ({ status: 'pending', reason: 'Waiting for input', processed: 0 })),
  );
  const [running, setRunning] = useState(false);
  const [done, setDone] = useState(false);
  const [summary, setSummary] = useState({ processed: 0, sent: 0, failed: 0 });
  const [activeCampaign, setActiveCampaign] = useState(null);
  const ran = useRef(false);

  // Load campaigns and auto-start
  useEffect(() => {
    if (ran.current) return;
    ran.current = true;
    loadAndRun();
  }, []);

  async function loadAndRun() {
    let campaigns = [];
    try {
      const data = await getJson('/campaigns');
      dispatch({ type: 'SET_CAMPAIGNS', payload: data });
      campaigns = data.campaigns || [];
    } catch {
      toast.error('Could not load campaigns.');
      return;
    }

    const selectedId = state.campaign?.upload?.campaign?.id || state.campaign?.id;
    const selected =
      campaigns.find((c) => c.id === selectedId && c.pendingCount > 0) ||
      campaigns.find((c) => c.pendingCount > 0) ||
      campaigns.find((c) => c.failedCount > 0);

    if (!selected) {
      toast.info('No pending campaign found. Upload a sheet first.');
      return;
    }

    setActiveCampaign(selected);
    await runCampaign(selected);
  }

  async function runCampaign(campaign) {
    const total = campaign.pendingCount || campaign.totalEmails || 0;
    const retryFailed = campaign.pendingCount === 0 && campaign.failedCount > 0;
    setRunning(true);
    setDone(false);
    setStepStatuses(STEP_NAMES.map(() => ({ status: 'pending', reason: 'Waiting for input', processed: 0 })));

    // Animate steps while API runs in background
    const apiPromise = postJson(
      `/campaigns/${campaign.id}/run`,
      { retryFailed },
      { timeout: CAMPAIGN_RUN_TIMEOUT_MS },
    );

    // Animate each step sequentially
    let elapsed = 0;
    for (let i = 0; i < STEP_NAMES.length; i++) {
      const duration = STEP_DURATIONS[i];
      // Mark step as active
      setStepStatuses((prev) => prev.map((s, idx) =>
        idx === i ? { ...s, status: 'active', processed: 0 } : s,
      ));
      // Animate progress within the step
      const ticks = 10;
      for (let t = 1; t <= ticks; t++) {
        await sleep(duration / ticks);
        const processed = Math.round((t / ticks) * total);
        setStepStatuses((prev) => prev.map((s, idx) =>
          idx === i ? { ...s, processed } : s,
        ));
      }
    }

    // Wait for actual API result
    let result;
    try {
      result = await apiPromise;
    } catch (err) {
      toast.error(err?.response?.data?.error || 'Campaign run failed.');
      setRunning(false);
      setStepStatuses((prev) => prev.map((s) => ({ ...s, status: s.status === 'active' ? 'failed' : s.status })));
      return;
    }

    // Apply real step results from API
    const stepMap = new Map((result.steps || []).map((s) => [s.name, s]));
    setStepStatuses(STEP_NAMES.map((name) => {
      const s = stepMap.get(name);
      return s
        ? { status: s.status || 'completed', reason: s.reason || `${name} completed`, processed: total }
        : { status: 'completed', reason: `${name} completed`, processed: total };
    }));

    dispatch({ type: 'SET_PIPELINE', payload: result.steps || [] });
    dispatch({ type: 'SET_SENT_EMAILS', payload: result.sentEmails || [] });
    dispatch({ type: 'SET_RESULTS', payload: result.summary || {} });
    if (result.campaign) {
      dispatch({ type: 'SET_CURRENT_CAMPAIGN', payload: { id: result.campaign.id, name: result.campaign.campaignName } });
    }

    const s = result.summary || {};
    setSummary({ processed: s.processed || 0, sent: s.sent || 0, failed: s.failed || 0 });
    setRunning(false);
    setDone(true);

    // Reload campaigns
    getJson('/campaigns').then((d) => dispatch({ type: 'SET_CAMPAIGNS', payload: d })).catch(() => {});

    if ((s.failed || 0) > 0) {
      toast.warning(`${s.failed} email(s) failed. Check Results for details.`);
    } else if ((s.sent || 0) > 0) {
      toast.success(`${s.sent} email(s) sent successfully!`);
    } else {
      toast.info('Pipeline finished. Check Results page.');
    }
  }

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  const total = activeCampaign?.pendingCount || activeCampaign?.totalEmails || 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h2 className="text-3xl font-bold text-slate-950">Pipeline execution</h2>
          <p className="mt-2 text-slate-500">
            {running
              ? `Running: ${activeCampaign?.campaignName} — processing ${total} email${total !== 1 ? 's' : ''}…`
              : done
              ? `Completed: ${summary.sent} sent, ${summary.failed} failed out of ${summary.processed} emails.`
              : activeCampaign
              ? `Ready: ${activeCampaign.campaignName} (${total} pending)`
              : 'Upload a campaign sheet to start.'}
          </p>
        </div>
        {done && (
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-emerald-50 px-4 py-2 text-sm font-semibold text-emerald-700">
              ✓ {summary.sent} Sent
            </div>
            {summary.failed > 0 && (
              <div className="rounded-lg bg-rose-50 px-4 py-2 text-sm font-semibold text-rose-700">
                ✗ {summary.failed} Failed
              </div>
            )}
          </div>
        )}
      </div>

      {/* Overall progress bar */}
      {running && (
        <div className="rounded-xl border border-blue-100 bg-blue-50 px-5 py-4">
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="font-medium text-blue-700">Pipeline running…</span>
            <span className="text-blue-600">
              {stepStatuses.filter((s) => s.status === 'completed').length}/{STEP_NAMES.length} steps
            </span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-blue-100">
            <div
              className="h-full rounded-full bg-blue-500 transition-all duration-700"
              style={{
                width: `${(stepStatuses.filter((s) => s.status === 'completed').length / STEP_NAMES.length) * 100}%`,
              }}
            />
          </div>
        </div>
      )}

      {/* Step grid */}
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        {STEP_NAMES.map((name, index) => (
          <StepCard
            key={name}
            name={name}
            index={index}
            status={stepStatuses[index].status}
            reason={stepStatuses[index].reason}
            processed={stepStatuses[index].processed}
            total={total}
          />
        ))}
      </div>

      {/* Summary cards */}
      {done && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <h3 className="font-semibold text-slate-700">Rows Processed</h3>
            <p className="mt-2 text-3xl font-bold text-slate-950">{summary.processed}</p>
          </Card>
          <Card>
            <h3 className="font-semibold text-emerald-600">Emails Sent</h3>
            <p className="mt-2 text-3xl font-bold text-emerald-700">{summary.sent}</p>
          </Card>
          <Card>
            <h3 className="font-semibold text-rose-600">Emails Failed</h3>
            <p className="mt-2 text-3xl font-bold text-rose-700">{summary.failed}</p>
          </Card>
        </div>
      )}

      {!running && !done && !activeCampaign && (
        <div className="rounded-xl border border-slate-200 bg-slate-50 py-12 text-center text-slate-500">
          No pending campaigns found. Go to <strong>Upload Links</strong> to upload a spreadsheet.
        </div>
      )}
    </div>
  );
}
