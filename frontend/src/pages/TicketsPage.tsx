import { FormEvent, useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { api } from '../api/client';
import { Ticket } from '../types';
import { wsEventsUrl } from '../lib/runtimeConfig';

export const TicketsPage = () => {
  const [items, setItems] = useState<Ticket[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const load = async () => { const { data } = await api.get('/tickets'); setItems(data); };
  useEffect(() => { load(); const ws = new WebSocket(wsEventsUrl()); ws.onmessage=()=>load(); return ()=>ws.close(); }, []);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const optimistic: Ticket = { id: Date.now(), title, description, status: 'open', priority: 'medium', assignee_id: null };
    setItems((v)=>[optimistic, ...v]);
    try { await api.post('/tickets', { title, description, category: 'general', priority: 'medium' }); toast.success('Ticket created'); setTitle(''); setDescription(''); await load(); }
    catch { toast.error('Failed'); setItems((v)=>v.filter((i)=>i.id!==optimistic.id)); }
  };

  return <div className='space-y-6'><form onSubmit={submit} className='bg-white p-4 rounded shadow space-y-2'><h2 className='font-semibold'>Create ticket</h2><input className='border p-2 w-full' value={title} onChange={(e)=>setTitle(e.target.value)} placeholder='Title' /><textarea className='border p-2 w-full' value={description} onChange={(e)=>setDescription(e.target.value)} placeholder='Description' /><button className='bg-emerald-600 text-white px-4 py-2 rounded'>Create</button></form><div className='grid gap-3'>{items.map((t)=><div key={t.id} className='bg-white border p-3 rounded'><div className='font-semibold'>{t.title}</div><div className='text-sm text-slate-600'>{t.description}</div><div className='text-xs mt-2'>{t.status} · {t.priority}</div></div>)}</div></div>;
};
