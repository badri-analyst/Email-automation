import StatusBadge from '../ui/StatusBadge.jsx';

export default function CampaignResultsTable({ rows = [] }) {
  return (
    <div className="overflow-auto rounded-xl border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
          <tr><th className="px-4 py-3">Prospect</th><th className="px-4 py-3">Recipient</th><th className="px-4 py-3">Decision</th><th className="px-4 py-3">Email</th><th className="px-4 py-3">Send</th><th className="px-4 py-3">Reason</th></tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((row, index) => (
            <tr key={`${row.prospect_id}-${index}`}>
              <td className="px-4 py-3">{row.prospect_id}</td>
              <td className="px-4 py-3">{row.recipient_email}</td>
              <td className="px-4 py-3"><StatusBadge status={row.decision_status}>{row.decision_status}</StatusBadge></td>
              <td className="px-4 py-3">{row.email_generation_status}</td>
              <td className="px-4 py-3"><StatusBadge status={row.send_status}>{row.send_status}</StatusBadge></td>
              <td className="max-w-lg px-4 py-3 text-slate-600">{row.send_reason || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
