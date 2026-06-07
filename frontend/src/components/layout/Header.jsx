import { LogOut, Menu, Moon, Search, UserCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.jsx';
import { useOutreach } from '../../context/OutreachContext.jsx';
import Button from '../ui/Button.jsx';

export default function Header({ onMenu }) {
  const { user, loading, signInWithGoogle, signOut } = useAuth();
  const { dispatch } = useOutreach();
  const navigate = useNavigate();

  function startNewCampaign() {
    dispatch({ type: 'RESET_CAMPAIGN_FLOW' });
    navigate('/upload');
  }

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 px-4 py-3 backdrop-blur lg:px-8">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden" onClick={onMenu}>
            <Menu size={20} />
          </button>
          <div className="hidden items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 md:flex">
            <Search size={16} className="text-slate-400" />
            <span className="text-sm text-slate-500">Search campaigns, emails, companies</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {user ? (
            <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-2 py-1.5">
              {user.avatarUrl ? (
                <img src={user.avatarUrl} alt="" className="h-7 w-7 rounded-full" referrerPolicy="no-referrer" />
              ) : (
                <UserCircle size={22} className="text-slate-500" />
              )}
              <div className="hidden min-w-0 sm:block">
                <p className="max-w-36 truncate text-sm font-semibold text-slate-800">{user.name}</p>
                <p className="max-w-36 truncate text-xs text-slate-500">{user.email}</p>
              </div>
              <button
                type="button"
                onClick={signOut}
                className="rounded-md p-1.5 text-slate-500 hover:bg-slate-100"
                title="Sign out"
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <Button variant="secondary" onClick={signInWithGoogle} disabled={loading}>
              {loading ? 'Checking...' : 'Sign in with Google'}
            </Button>
          )}
          <Button variant="ghost" title="Theme toggle is UI-only for now">
            <Moon size={16} />
          </Button>
          <Button onClick={startNewCampaign}>New campaign</Button>
        </div>
      </div>
    </header>
  );
}
