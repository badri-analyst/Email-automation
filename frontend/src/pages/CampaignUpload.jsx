import Card from '../components/ui/Card.jsx';
import UploadForm from '../components/forms/UploadForm.jsx';
import ValidationTable from '../components/tables/ValidationTable.jsx';
import { useOutreach } from '../context/OutreachContext.jsx';

export default function CampaignUpload() {
  const { state } = useOutreach();
  const validation = state.campaign.validation || {};
  const rows = state.campaign.upload?.rows || [];
  return (
    <div className="space-y-6">
      <div><h2 className="text-3xl font-bold text-slate-950">Upload links</h2><p className="mt-2 text-slate-500">Upload CSV/XLSX recruiter or company sheets and review validation outcomes.</p></div>
      <Card><UploadForm /></Card>
      <div className="grid gap-4 md:grid-cols-4">
        {[
          ['Total rows', validation.total_rows],
          ['Valid rows', validation.valid_rows],
          ['Invalid rows', validation.invalid_rows],
          ['Duplicate rows', validation.duplicate_rows],
        ].map(([label, value]) => <Card key={label}><p className="text-sm text-slate-500">{label}</p><p className="mt-2 text-2xl font-bold">{value || 0}</p></Card>)}
      </div>
      <ValidationTable rows={rows} />
    </div>
  );
}
