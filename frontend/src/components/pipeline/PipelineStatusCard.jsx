import Card from '../ui/Card.jsx';
import StatusBadge from '../ui/StatusBadge.jsx';

export default function PipelineStatusCard({ title, status, description }) {
  return (
    <Card>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-semibold text-slate-900">{title}</h3>
          <p className="mt-1 text-sm text-slate-500">{description}</p>
        </div>
        <StatusBadge status={status}>{status}</StatusBadge>
      </div>
    </Card>
  );
}
