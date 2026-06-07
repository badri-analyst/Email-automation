import { LogOut, UserCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';
import Card from '../components/ui/Card.jsx';
import Button from '../components/ui/Button.jsx';

export default function Account() {
  const { user, signOut } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-slate-950">Account</h2>
        <p className="mt-2 text-slate-500">Manage your signed-in profile and session.</p>
      </div>
      <Card>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            {user?.avatarUrl ? (
              <img src={user.avatarUrl} alt="" className="h-12 w-12 rounded-full" referrerPolicy="no-referrer" />
            ) : (
              <UserCircle size={48} className="text-slate-400" />
            )}
            <div>
              <p className="font-semibold text-slate-950">{user?.name}</p>
              <p className="text-sm text-slate-500">{user?.email}</p>
            </div>
          </div>
          <Button variant="secondary" onClick={signOut}>
            <LogOut size={16} />
            Sign out
          </Button>
        </div>
      </Card>
    </div>
  );
}
