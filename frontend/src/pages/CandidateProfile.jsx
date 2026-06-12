import { useLocation } from 'react-router-dom';
import Card from '../components/ui/Card.jsx';
import CandidateForm from '../components/forms/CandidateForm.jsx';

export default function CandidateProfile() {
  const location = useLocation();
  const gmailReconnect = location.state?.gmailReconnect || false;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-slate-950">Candidate details</h2>
        <p className="mt-2 text-slate-500">Store reusable candidate assets, proof points, and outreach-safe positioning.</p>
      </div>

      {gmailReconnect && (
        <div className="flex items-start gap-4 rounded-xl border border-amber-200 bg-amber-50 px-5 py-4">
          <div className="flex-1">
            <p className="font-semibold text-amber-700">Gmail reconnection required</p>
            <p className="mt-1 text-sm text-amber-600">
              Your Gmail session has expired or was disconnected. Scroll down to the Gmail section and reconnect your account before running the campaign again.
            </p>
          </div>
          <span className="shrink-0 rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700">
            Action needed
          </span>
        </div>
      )}

      <Card><CandidateForm highlightGmail={gmailReconnect} /></Card>
    </div>
  );
}
