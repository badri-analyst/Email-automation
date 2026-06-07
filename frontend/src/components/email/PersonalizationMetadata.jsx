import StatusBadge from '../ui/StatusBadge.jsx';

export default function PersonalizationMetadata({ email }) {
  const meta = email.personalization_used || {};
  const sources = email.sources_used || {};
  return (
    <div className="grid gap-3 text-sm md:grid-cols-2">
      {Object.entries(meta).map(([key, value]) => (
        <div key={key} className="rounded-lg bg-slate-50 p-3">
          <p className="text-xs font-semibold uppercase text-slate-400">{key.replaceAll('_', ' ')}</p>
          <p className="mt-1 text-slate-700">{value || 'Not used'}</p>
        </div>
      ))}
      <div className="rounded-lg bg-slate-50 p-3 md:col-span-2">
        <p className="mb-2 text-xs font-semibold uppercase text-slate-400">Sources used</p>
        <div className="flex flex-wrap gap-2">
          {Object.entries(sources).map(([key, value]) => (
            <StatusBadge key={key} status={value ? 'success' : 'pending'}>{key.replaceAll('_', ' ')}</StatusBadge>
          ))}
        </div>
      </div>
    </div>
  );
}
