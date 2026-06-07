import React from 'react';
import ReactDOM from 'react-dom/client';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import App from './App.jsx';
import { AuthProvider } from './context/AuthContext.jsx';
import { OutreachProvider } from './context/OutreachContext.jsx';
import './styles/global.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <OutreachProvider>
        <App />
        <ToastContainer position="top-right" autoClose={2800} hideProgressBar />
      </OutreachProvider>
    </AuthProvider>
  </React.StrictMode>,
);
