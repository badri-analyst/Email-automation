import { NavLink } from 'react-router-dom';
import { BarChart3, FolderKanban, FileSpreadsheet, Rocket, Settings, UserRound } from 'lucide-react';

const links = [
  { to: '/candidate', label: 'Candidate Details', icon: UserRound },
  { to: '/upload', label: 'Upload Links', icon: FileSpreadsheet },
  { to: '/pipeline', label: 'Pipeline', icon: Rocket },
  { to: '/dashboard', label: 'Dashboard', icon: BarChart3 },
  { to: '/campaigns', label: 'Campaigns', icon: FolderKanban },
  { to: '/account', label: 'Account', icon: Settings },
];

export default function Sidebar({ open, onClose }) {
  return (
    <aside className={`${open ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-40 w-72 border-r border-slate-200 bg-white p-4 transition lg:static lg:translate-x-0`}>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-brand-600">Outreach AI</p>
          <h1 className="text-xl font-bold text-slate-950">Recruiter Pipeline</h1>
        </div>
        <button className="lg:hidden" onClick={onClose}>×</button>
      </div>
      <nav className="space-y-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onClose}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${isActive ? 'bg-brand-50 text-brand-700' : 'text-slate-600 hover:bg-slate-50'}`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
