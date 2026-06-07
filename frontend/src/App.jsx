import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import DashboardLayout from './components/layout/DashboardLayout.jsx';
import ProtectedRoute from './routes/ProtectedRoute.jsx';
import Dashboard from './pages/Dashboard.jsx';
import CandidateProfile from './pages/CandidateProfile.jsx';
import CampaignUpload from './pages/CampaignUpload.jsx';
import PipelineExecution from './pages/PipelineExecution.jsx';
import CampaignResults from './pages/CampaignResults.jsx';
import Login from './pages/Login.jsx';
import Account from './pages/Account.jsx';
import Campaigns from './pages/Campaigns.jsx';
import GmailCallback from './pages/GmailCallback.jsx';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        {/* OAuth2 callback — must be accessible without wrapping in ProtectedRoute
            so the redirect from Google lands correctly */}
        <Route path="/gmail-callback" element={<GmailCallback />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route index element={<Navigate to="/candidate" replace />} />
            <Route path="/candidate" element={<CandidateProfile />} />
            <Route path="/upload" element={<CampaignUpload />} />
            <Route path="/pipeline" element={<PipelineExecution />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/account" element={<Account />} />
            <Route path="/results" element={<CampaignResults />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/candidate" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
