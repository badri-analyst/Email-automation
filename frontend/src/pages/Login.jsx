import { Navigate } from 'react-router-dom';
import { MailCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';
import Button from '../components/ui/Button.jsx';

export default function Login() {
  const { user, loading, signInWithGoogle } = useAuth();

  if (user) return <Navigate to="/candidate" replace />;

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-brand-50 text-brand-700">
          <MailCheck size={24} />
        </div>
        <h1 className="text-2xl font-bold text-slate-950">Sign in to Outreach AI</h1>
        <p className="mt-2 text-sm text-slate-500">
          Use Google to access your candidate profile, uploaded campaign data, and sending workflow.
        </p>
        <Button className="mt-6 w-full justify-center" onClick={signInWithGoogle} disabled={loading}>
          {loading ? 'Checking session...' : 'Sign in with Google'}
        </Button>
      </div>
    </div>
  );
}
