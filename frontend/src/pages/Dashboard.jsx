import { Link } from 'react-router-dom';
import { AlertTriangle, CheckCircle2, FileUp, Mail, Users } from 'lucide-react';
import Card from '../components/ui/Card.jsx';
import Button from '../components/ui/Button.jsx';
import PipelineStepper from '../components/pipeline/PipelineStepper.jsx';
import EmailPreviewCard from '../components/email/EmailPreviewCard.jsx';
import { useOutreach } from '../context/OutreachContext.jsx';

function Metric({ label, value, icon: Icon }) {
  return (
    <Card>
      <div className="flex items-center justify-between">
        <div><p className="text-sm text-slate-500">{label}</p><p className="mt-2 text-3xl font-bold text-slate-950">{value}</p></div>
        <div className="rounded-xl bg-brand-50 p-3 text-brand-600"><Icon size={22} /></div>
      </div>
    </Card>
  );
}

export default function Dashboard() {
  const { state } = useOutreach();
  const validation = state.campaign.validation || {};
  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="text-sm font-semibold text-brand-600">Campaign overview</p>
          <h2 className="text-3xl font-bold text-slate-950">Recruiter outreach dashboard</h2>
          <p className="mt-2 max-w-2xl text-slate-500">Upload leads, run the pipeline, and send recruiter emails directly through Gmail.</p>
        </div>
        <Link to="/upload"><Button><FileUp size={16} /> Upload spreadsheet</Button></Link>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
        <Metric label="Uploaded Leads" value={validation.total_rows || 0} icon={Users} />
        <Metric label="Valid Leads" value={validation.valid_rows || 0} icon={CheckCircle2} />
        <Metric label="Emails Generated" value={state.sentEmails.length} icon={Mail} />
        <Metric label="Emails Sent" value={state.sentEmails.filter((d) => d.send_status === 'sent').length} icon={CheckCircle2} />
        <Metric label="Send Failures" value={state.sentEmails.filter((d) => d.send_status === 'send_failed').length} icon={AlertTriangle} />
        <Metric label="Failed Rows" value={validation.invalid_rows || 0} icon={AlertTriangle} />
      </div>
      <PipelineStepper steps={state.pipeline} />
      <section>
        <h3 className="mb-3 text-lg font-semibold text-slate-900">Recent sent emails</h3>
        <div className="grid gap-4 lg:grid-cols-3">
          {state.sentEmails.slice(0, 3).map((email) => <EmailPreviewCard key={email.prospect_id || email.subject_line} email={email} />)}
          {state.sentEmails.length === 0 && <Card className="lg:col-span-3"><p className="text-slate-500">No sent emails yet. Run the pipeline to generate and send recruiter emails.</p></Card>}
        </div>
      </section>
    </div>
  );
}
