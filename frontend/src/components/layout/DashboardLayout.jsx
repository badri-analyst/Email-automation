import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar.jsx';
import Header from './Header.jsx';

export default function DashboardLayout() {
  const [open, setOpen] = useState(false);
  return (
    <div className="min-h-screen bg-slate-50 lg:flex">
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <div className="min-w-0 flex-1">
        <Header onMenu={() => setOpen(true)} />
        <main className="mx-auto max-w-7xl p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
