import { createContext, useContext, useEffect, useMemo, useReducer } from 'react';
import { useAuth } from './AuthContext.jsx';

const OutreachContext = createContext(null);
const STORAGE_KEY = 'outreach_ai_state_v1';

const initialState = {
  candidate: {},
  campaign: {
    id: 'campaign-demo',
    upload: null,
    validation: null,
    rows: [],
    pipelineResults: [],
  },
  pipeline: [],
  sentEmails: [],
  results: {},
  campaigns: [],
  campaignSummary: {
    totalCampaigns: 0,
    totalEmailsUploaded: 0,
    totalEmailsSent: 0,
    totalEmailsFailed: 0,
    totalEmailsPending: 0,
  },
};

function removeSensitiveCandidateFields(candidate = {}) {
  // Strip any legacy credential fields that must never be persisted to localStorage.
  const { googleAppPassword: _g, refreshToken: _r, ...safeCandidate } = candidate;
  return safeCandidate;
}

function userStorageKey(user) {
  return user?.email ? `${STORAGE_KEY}:${user.email.toLowerCase()}` : STORAGE_KEY;
}

function loadStoredState(user) {
  if (typeof window === 'undefined') return initialState;
  try {
    const stored = JSON.parse(window.localStorage.getItem(userStorageKey(user)) || '{}');
    return {
      ...initialState,
      ...stored,
      candidate: removeSensitiveCandidateFields(stored.candidate || {}),
      campaign: { ...initialState.campaign, ...(stored.campaign || {}) },
    };
  } catch (_error) {
    return initialState;
  }
}

function persistState(state, user) {
  if (typeof window === 'undefined') return;
  if (!user?.email) return;
  // Exclude large/transient arrays that should not survive a page refresh.
  const { sentEmails: _s, pipeline: _p, ...persistable } = state;
  const safeState = {
    ...persistable,
    candidate: removeSensitiveCandidateFields(persistable.candidate),
  };
  window.localStorage.setItem(userStorageKey(user), JSON.stringify(safeState));
}

function reducer(state, action) {
  let nextState;
  switch (action.type) {
    case 'SET_CANDIDATE':
      nextState = { ...state, candidate: { ...state.candidate, ...action.payload } };
      break;
    case 'SET_UPLOAD':
      nextState = {
        ...state,
        campaign: {
          ...state.campaign,
          id: action.payload?.campaign?.id || state.campaign.id,
          name: action.payload?.campaign?.campaignName || state.campaign.name,
          upload: action.payload,
        },
      };
      break;
    case 'SET_VALIDATION':
      nextState = { ...state, campaign: { ...state.campaign, validation: action.payload } };
      break;
    case 'SET_PIPELINE':
      nextState = { ...state, pipeline: action.payload };
      break;
    case 'SET_SENT_EMAILS':
      nextState = { ...state, sentEmails: action.payload };
      break;
    case 'SET_RESULTS':
      nextState = { ...state, results: action.payload };
      break;
    case 'SET_CAMPAIGNS':
      nextState = { ...state, campaigns: action.payload?.campaigns || [], campaignSummary: action.payload?.summary || initialState.campaignSummary };
      break;
    case 'SET_CURRENT_CAMPAIGN':
      nextState = { ...state, campaign: { ...state.campaign, ...action.payload } };
      break;
    case 'RESET_CAMPAIGN_FLOW':
      nextState = {
        ...state,
        campaign: { ...initialState.campaign, id: `campaign-${Date.now()}` },
        pipeline: [],
        sentEmails: [],
        results: {},
      };
      break;
    case 'RESET_STATE':
      nextState = initialState;
      break;
    case 'HYDRATE_STATE':
      nextState = action.payload || initialState;
      break;
    default:
      nextState = state;
  }
  return nextState;
}

export function OutreachProvider({ children }) {
  const { user } = useAuth();
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    if (!user?.email) {
      if (typeof window !== 'undefined') {
        // Remove both the legacy bare key and every user-scoped key.
        window.localStorage.removeItem(STORAGE_KEY);
        Object.keys(window.localStorage)
          .filter((k) => k.startsWith(`${STORAGE_KEY}:`))
          .forEach((k) => window.localStorage.removeItem(k));
      }
      dispatch({ type: 'RESET_STATE' });
      return;
    }
    dispatch({ type: 'HYDRATE_STATE', payload: loadStoredState(user) });
  }, [user?.email]);

  useEffect(() => {
    persistState(state, user);
  }, [state, user?.email]);

  const value = useMemo(() => ({ state, dispatch }), [state]);
  return <OutreachContext.Provider value={value}>{children}</OutreachContext.Provider>;
}

export function useOutreach() {
  const context = useContext(OutreachContext);
  if (!context) throw new Error('useOutreach must be used inside OutreachProvider');
  return context;
}
