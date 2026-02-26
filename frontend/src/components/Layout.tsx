import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Layout = ({children}:{children:React.ReactNode}) => {
  const {logout}=useAuth();
  return <div className='min-h-screen'><header className='bg-slate-900 text-white p-4 flex gap-4'><Link to='/'>Tickets</Link><Link to='/admin'>Admin</Link><button className='ml-auto' onClick={logout}>Logout</button></header><main className='p-4 max-w-5xl mx-auto'>{children}</main></div>;
};
