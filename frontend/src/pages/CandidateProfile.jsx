import Card from '../components/ui/Card.jsx';
import CandidateForm from '../components/forms/CandidateForm.jsx';

export default function CandidateProfile() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-slate-950">Candidate details</h2>
        <p className="mt-2 text-slate-500">Store reusable candidate assets, proof points, and outreach-safe positioning.</p>
      </div>
      <Card><CandidateForm /></Card>
    </div>
  );
}
