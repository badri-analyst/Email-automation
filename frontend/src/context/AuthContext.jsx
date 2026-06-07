import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { toast } from 'react-toastify';
import { isAuthConfigured, supabaseAuth } from '../services/supabaseAuth.js';

const AuthContext = createContext(null);

function toUser(session) {
  const user = session?.user;
  if (!user) return null;
  return {
    id: user.id,
    email: user.email || '',
    name: user.user_metadata?.full_name || user.user_metadata?.name || user.email || 'Signed-in user',
    avatarUrl: user.user_metadata?.avatar_url || '',
  };
}

function clearUserScopedStorage() {
  Object.keys(window.localStorage)
    .filter((key) => key === 'outreach_ai_state_v1' || key.startsWith('outreach_ai_state_v1:'))
    .forEach((key) => window.localStorage.removeItem(key));
  window.sessionStorage.clear();
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(supabaseAuth));

  useEffect(() => {
    if (!supabaseAuth) {
      setLoading(false);
      return undefined;
    }

    let mounted = true;
    supabaseAuth.auth.getSession().then(({ data }) => {
      if (!mounted) return;
      setUser(toUser(data.session));
      setLoading(false);
    });

    const { data: listener } = supabaseAuth.auth.onAuthStateChange((_event, session) => {
      if (!session) clearUserScopedStorage();
      setUser(toUser(session));
      setLoading(false);
    });

    return () => {
      mounted = false;
      listener.subscription.unsubscribe();
    };
  }, []);

  async function signInWithGoogle() {
    if (!isAuthConfigured()) {
      toast.error('Google sign-in is not configured. Add Supabase URL and publishable key in Vercel.');
      return;
    }
    const { error } = await supabaseAuth.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/candidate`,
        queryParams: {
          access_type: 'offline',
          prompt: 'select_account',
        },
      },
    });
    if (error) toast.error(error.message);
  }

  async function signOut() {
    if (!supabaseAuth) return;
    const { error } = await supabaseAuth.auth.signOut();
    if (error) toast.error(error.message);
    else {
      setUser(null);
      clearUserScopedStorage();
    }
  }

  const value = useMemo(() => ({
    user,
    loading,
    signInWithGoogle,
    signOut,
    authConfigured: isAuthConfigured(),
  }), [user, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside AuthProvider');
  return context;
}
