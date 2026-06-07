import StatusBadge from '../ui/StatusBadge.jsx';

export default function ValidationTable({ rows = [] }) {
  const hasLinkedIn = rows.some((row) => row.linkedin_url || row.LinkedIn || row['LinkedIn URL']);
  const hasWebsite = rows.some((row) => row.company_website || row.Website || row.website);
  const columns = [
    ['Name', (row) => row.Name || row.name],
    ['Email', (row) => row.Email || row.email],
    ['Company', (row) => row.Company || row.company],
    ...(hasLinkedIn ? [['LinkedIn', (row) => row.linkedin_url || row.LinkedIn || row['LinkedIn URL']]] : []),
    ...(hasWebsite ? [['Website', (row) => row.company_website || row.Website || row.website]] : []),
    ['Role', (row) => row.Role || row.role],
    ['Country', (row) => row.Country || row.country],
  ];

  return (
    <div className="overflow-auto rounded-xl border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
          <tr>
            {columns.map(([header]) => <th key={header} className="px-4 py-3">{header}</th>)}
            <th className="px-4 py-3">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((row, index) => (
            <tr key={`${row.Email || row.email}-${index}`}>
              {columns.map(([header, getValue]) => (
                <td key={header} className="max-w-72 truncate px-4 py-3" title={getValue(row) || ''}>{getValue(row) || '-'}</td>
              ))}
              <td className="px-4 py-3"><StatusBadge status={row.validation_status || 'pending'}>{row.validation_status || 'pending'}</StatusBadge></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
