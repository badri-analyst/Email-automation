import StatusBadge from '../ui/StatusBadge.jsx';

export const pipelineSteps = [
  'Validation',
  'Cleaning',
  'Role-Country Intelligence',
  'LinkedIn Research',
  'Company Research',
  'Communication Signals',
  'Candidate Assets',
  'Decision Engine',
  'Email Generation',
  'SMTP Send',
];

export default function PipelineStepper({ steps = [] }) {
  const map = new Map(steps.map((step) => [step.name, step]));
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
      {pipelineSteps.map((name, index) => {
        const step = map.get(name) || { status: 'pending' };
        return (
          <div key={name} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-soft">
            <div className="mb-3 flex items-center justify-between">
              <span className="grid h-8 w-8 place-items-center rounded-full bg-slate-100 text-sm font-semibold text-slate-600">{index + 1}</span>
              <StatusBadge status={step.status}>{step.status}</StatusBadge>
            </div>
            <p className="text-sm font-semibold text-slate-900">{name}</p>
            <p className="mt-1 text-xs text-slate-500">{step.reason || 'Waiting for input'}</p>
          </div>
        );
      })}
    </div>
  );
}
