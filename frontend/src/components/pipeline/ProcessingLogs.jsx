import Card from '../ui/Card.jsx';

export default function ProcessingLogs({ logs = [] }) {
  return (
    <Card>
      <h3 className="mb-3 font-semibold text-slate-900">Processing logs</h3>
      <div className="max-h-80 space-y-2 overflow-auto text-sm">
        {logs.length === 0 ? <p className="text-slate-500">No logs yet.</p> : logs.map((log, index) => (
          <details key={`${log.message}-${index}`} className="rounded-lg bg-slate-50 p-3">
            <summary className="cursor-pointer font-medium text-slate-700">{log.stage} · {log.status}</summary>
            <p className="mt-2 text-slate-500">{log.message}</p>
          </details>
        ))}
      </div>
    </Card>
  );
}
