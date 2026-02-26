import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import './index.css';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/Layout';
import { LoginPage } from './pages/LoginPage';
import { TicketsPage } from './pages/TicketsPage';
import { AdminPage } from './pages/AdminPage';

const Protected = ({ children }: { children: React.ReactNode }) => {
  const { token } = useAuth();
  if (!token) return <Navigate to='/login' replace />;
  return <Layout>{children}</Layout>;
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Toaster position='top-right' />
        <Routes>
          <Route path='/login' element={<LoginPage />} />
          <Route path='/' element={<Protected><TicketsPage /></Protected>} />
          <Route path='/admin' element={<Protected><AdminPage /></Protected>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
);
