import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export const LoginPage = () => {
  const [email, setEmail] = useState('admin@helpdesk.local');
  const [password, setPassword] = useState('Admin123!');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const nav = useNavigate();

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.post('/auth/login', { email, password });
      login(data.access_token);
      toast.success('Logged in');
      nav('/');
    } catch {
      toast.error('Invalid credentials');
    } finally { setLoading(false); }
  };

  return <div className='min-h-screen grid place-items-center'><form onSubmit={onSubmit} className='bg-white p-6 rounded-xl shadow w-96 space-y-4'><h1 className='text-xl font-bold'>Helpdesk Login</h1><input className='border p-2 w-full' value={email} onChange={(e)=>setEmail(e.target.value)} /><input className='border p-2 w-full' type='password' value={password} onChange={(e)=>setPassword(e.target.value)} /><button disabled={loading} className='bg-blue-600 text-white px-4 py-2 rounded w-full'>{loading?'Loading...':'Sign in'}</button></form></div>;
};
