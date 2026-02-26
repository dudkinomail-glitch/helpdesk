import { FormEvent, useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { api } from '../api/client';

export const AdminPage = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('User123!');
  const [role, setRole] = useState('support');
  const load = async()=>{ const {data}=await api.get('/admin/users'); setUsers(data); };
  useEffect(()=>{ load(); },[]);
  const submit = async (e:FormEvent)=>{ e.preventDefault(); try { await api.post('/admin/users', { email, full_name: fullName, password, role }); toast.success('User created'); setEmail(''); setFullName(''); load(); } catch { toast.error('Need admin role'); } };
  return <div className='space-y-4'><form onSubmit={submit} className='bg-white p-4 rounded shadow grid md:grid-cols-4 gap-2'><input className='border p-2' placeholder='Email' value={email} onChange={(e)=>setEmail(e.target.value)} /><input className='border p-2' placeholder='Full name' value={fullName} onChange={(e)=>setFullName(e.target.value)} /><select className='border p-2' value={role} onChange={(e)=>setRole(e.target.value)}><option value='user'>user</option><option value='support'>support</option><option value='admin'>admin</option></select><button className='bg-indigo-600 text-white rounded px-3'>Add user</button></form><div className='bg-white rounded shadow'><table className='w-full text-sm'><thead><tr className='text-left border-b'><th className='p-2'>ID</th><th>Email</th><th>Name</th><th>Role</th></tr></thead><tbody>{users.map((u)=><tr key={u.id} className='border-b'><td className='p-2'>{u.id}</td><td>{u.email}</td><td>{u.full_name}</td><td>{u.role}</td></tr>)}</tbody></table></div></div>;
};
