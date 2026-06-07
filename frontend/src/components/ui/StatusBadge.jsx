const styles = {
  completed: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  success: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  active: 'bg-blue-50 text-blue-700 ring-blue-200',
  failed: 'bg-rose-50 text-rose-700 ring-rose-200',
  warning: 'bg-amber-50 text-amber-700 ring-amber-200',
  pending: 'bg-slate-50 text-slate-600 ring-slate-200',
  skipped: 'bg-slate-100 text-slate-500 ring-slate-200',
  Uploaded: 'bg-blue-50 text-blue-700 ring-blue-200',
  Processing: 'bg-amber-50 text-amber-700 ring-amber-200',
  Completed: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  Failed: 'bg-rose-50 text-rose-700 ring-rose-200',
  'Partially Completed': 'bg-amber-50 text-amber-700 ring-amber-200',
};

export default function StatusBadge({ status = 'pending', children }) {
  const key = String(status).includes('failed') || String(status).includes('blocked') ? 'failed' : status;
  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ring-1 ${styles[key] || styles.pending}`}>
      {children || status}
    </span>
  );
}
