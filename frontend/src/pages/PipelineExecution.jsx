import { useEffect, useRef, useState, useCallback } from 'react';
import { toast } from 'react-toastify';
import { getJson, postJson } from '../services/api.js';
import { useOutreach } from '../context/OutreachContext.jsx';
import Card from '../components/ui/Card.jsx';
import StatusBadge from '../components/ui/StatusBadge.jsx';
import { useNavigate } from 'react-router-dom';

const POLL_INTERVAL_MS = 8000; // poll every 8s — 200 emails takes ~20 min on free tier

const STEP_NAMES = [
  'Validation',
  'Cleaning',
  'Role-Country Intelligence',
  'LinkedIn Research',
  'Company Research',
  'Candidate Assets',
  'Decision Engine',
  'Email Generation',
  'Gmail Send',
];

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
  const navigate = useNavigate();
  const [gmailError, setGmailError] = useState(false);
  const [stepStatuses, setStepStatuses] = useState(
    STEP_NAMES.map(() => ({ status: 'pending', reason: 'Waiting for input', processed: 0 })),
  );
  const [running, setRunning] = useState(false);
  const [done, setDone] = useState(false);
  const [summary, setSummary] = useState({ processed: 0, sent: 0, failed: 0 });
  const [activeCampaign, setActiveCampaign] = useState(null);
  const ran = useRef(false);
  const pollRef = useRef(null);
  const campaignIdRef = useRef(null);

  useEffect(() => {
    if (ran.current) return;
    ran.current = true;
    loadAndRun();
  }, []);

  // Cleanup poll on unmount
  useEffect(() => {
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
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
    const alreadyDone = ['Completed', 'Partially Completed', 'Failed', 'No Recipients'];

    const selected =
      campaigns.find((c) => c.id === selectedId && c.pendingCount > 0) ||
      campaigns.find((c) => c.pendingCount > 0);

    if (!selected) {
      // Check if the latest campaign is already done — show results without re-running
      const latest = campaigns.find((c) => c.id === selectedId) || campaigns[0];
      if (latest && alreadyDone.includes(latest.status)) {
        setActiveCampaign(latest);
        setSummary({ processed: latest.totalEmails || 0, sent: latest.sentCount || 0, failed: latest.failedCount || 0 });
        setStepStatuses(STEP_NAMES.map(() => ({ status: 'completed', reason: 'Completed', processed: latest.totalEmails || 0 })));
        setDone(true);
        return;
      }
      toast.info('No pending campaign found. Upload a sheet first.');
      return;
    }

    setActiveCampaign(selected);
    await startCampaign(selected);
  }

  async function startCampaign(campaign) {
    const total = campaign.pendingCount || campaign.totalEmails || 0;
    const retryFailed = campaign.pendingCount === 0 && campaign.failedCount > 0;

    setRunning(true);
    setDone(false);
    setSummary({ processed: 0, sent: 0, failed: total });
    setStepStatuses(STEP_NAMES.map((_, i) =>
      i === 0 ? { status: 'active', reason: 'Processing…', processed: 0 }
              : { status: 'pending', reason: 'Waiting for input', processed: 0 },
    ));

    campaignIdRef.current = campaign.id;

    // Fire the run request — backend responds immediately and processes in background
    try {
      await postJson(`/campaigns/${campaign.id}/run`, { retryFailed });
    } catch (err) {
      const errorCode = err?.response?.data?.error_code;
      if (errorCode === 'GMAIL_AUTH_REQUIRED') {
        setGmailError(true);
        setRunning(false);
        return;
      }
      toast.error(err?.response?.data?.error || 'Failed to start campaign.');
      setRunning(false);
      return;
    }

    // Start polling for live progress
    startPolling(campaign.id, total);
  }

  function startPolling(campaignId, total) {
    if (pollRef.current) clearInterval(pollRef.current);

    pollRef.current = setInterval(async () => {
      try {
        const data = await getJson(`/campaigns/${campaignId}`);
        const c = data.campaign;
        if (!c) return;

        const sent = c.sentCount || 0;
        const failed = c.failedCount || 0;
        const processed = sent + failed;
        const total_ = c.totalEmails || total;

        // Derive which "step" we appear to be on based on progress ratio
        const ratio = total_ > 0 ? processed / total_ : 0;
        const activeStepIdx = Math.min(Math.floor(ratio * (STEP_NAMES.length - 1)), STEP_NAMES.length - 1);

        setStepStatuses(STEP_NAMES.map((_, idx) => {
          if (idx < activeStepIdx) return { status: 'completed', reason: 'Completed', processed: total_ };
          if (idx === activeStepIdx) return { status: 'active', reason: 'Processing…', processed };
          return { status: 'pending', reason: 'Waiting for input', processed: 0 };
        }));

        setSummary({ processed, sent, failed });
        setActiveCampaign(c);

        // Done when campaign status is terminal or all emails accounted for
        const terminalStatuses = ['Completed', 'Partially Completed', 'Failed', 'No Recipients'];
        const isDone = terminalStatuses.includes(c.status)
          || (total_ > 0 && processed >= total_)
          || (total_ === 0 && c.status !== 'Processing');

        if (isDone) {
          clearInterval(pollRef.current);
          pollRef.current = null;

          // Mark all steps completed
          setStepStatuses(STEP_NAMES.map(() => ({ status: 'completed', reason: 'Completed', processed: total_ })));
          setSummary({ processed: total_, sent, failed });
          setRunning(false);
          setDone(true);

          dispatch({ type: 'SET_RESULTS', payload: { processed: total_, sent, failed } });
          getJson('/campaigns').then((d) => dispatch({ type: 'SET_CAMPAIGNS', payload: d })).catch(() => {});

          if (failed > 0 && sent === 0) {
            toast.error(`All ${failed} emails failed. Check Campaigns for details.`);
          } else if (failed > 0) {
            toast.warning(`${sent} sent, ${failed} failed.`);
          } else {
            toast.success(`${sent} email${sent !== 1 ? 's' : ''} sent successfully!`);
          }
        }
      } catch {
        // Ignore transient poll errors
      }
    }, POLL_INTERVAL_MS);
  }

  const total = activeCampaign?.totalEmails || activeCampaign?.pendingCount || 0;
  const completedSteps = stepStatuses.filter((s) => s.status === 'completed').length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h2 className="text-3xl font-bold text-slate-950">Pipeline execution</h2>
          <p className="mt-2 text-slate-500">
            {running
              ? `Processing ${summary.processed}/${total} emails… (${summary.sent} sent, ${summary.failed} failed)`
              : done
              ? `Completed: ${summary.sent} sent, ${summary.failed} failed out of ${total} emails.`
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

      {/* Large campaign warning */}
      {running && total >= 50 && summary.processed === 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-5 py-3 text-sm text-amber-700">
          <strong>{total} emails detected.</strong> Estimated time: ~{Math.ceil(total / 2 * 12 / 60)} minutes on free tier. Keep this tab open — processing continues in the background.
        </div>
      )}

      {/* Overall progress bar */}
      {running && (
        <div className="rounded-xl border border-blue-100 bg-blue-50 px-5 py-4">
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="font-medium text-blue-700">Pipeline running… emails are being processed in the background</span>
            <span className="text-blue-600">{summary.processed}/{total} emails</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-blue-100">
            <div
              className="h-full rounded-full bg-blue-500 transition-all duration-700"
              style={{ width: total > 0 ? `${Math.round((summary.processed / total) * 100)}%` : '5%' }}
            />
          </div>
        </div>
      )}

      {/* Gmail re-login banner */}
      {gmailError && (
        <div className="flex items-start gap-4 rounded-xl border border-rose-200 bg-rose-50 px-5 py-4">
          <div className="flex-1">
            <p className="font-semibold text-rose-700">Gmail session expired or not connected</p>
            <p className="mt-1 text-sm text-rose-600">
              Your Gmail account needs to be reconnected before sending emails. Please re-login and try again.
            </p>
          </div>
          <button
            onClick={() => navigate('/candidate-profile', { state: { gmailReconnect: true } })}
            className="shrink-0 rounded-lg bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700"
          >
            Reconnect Gmail
          </button>
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
      {(running || done) && (
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
