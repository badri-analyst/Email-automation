import Card from '../ui/Card.jsx';
import StatusBadge from '../ui/StatusBadge.jsx';

export default function EmailPreviewCard({ email }) {
  return (
    <Card className="transition hover:-translate-y-0.5">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold text-slate-900">{email.subject_line || 'Sent email'}</h3>
          <p className="text-sm text-slate-500">{email.recipient_email} · {email.word_count || 0} words</p>
        </div>
        <StatusBadge status={email.send_status}>{email.send_status}</StatusBadge>
      </div>
      <p className="line-clamp-4 whitespace-pre-line text-sm text-slate-600">{email.email_body}</p>
    </Card>
  );
}
