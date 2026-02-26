import { createContext, useContext, useState } from 'react';

interface AuthState { token: string | null; login: (t:string)=>void; logout:()=>void; }
const AuthContext = createContext<AuthState>({ token:null, login:()=>{}, logout:()=>{} });
export const AuthProvider = ({children}:{children:React.ReactNode}) => {
  const [token, setToken] = useState<string|null>(localStorage.getItem('access_token'));
  const login=(t:string)=>{ localStorage.setItem('access_token', t); setToken(t); };
  const logout=()=>{ localStorage.removeItem('access_token'); setToken(null); };
  return <AuthContext.Provider value={{token,login,logout}}>{children}</AuthContext.Provider>;
};
export const useAuth=()=>useContext(AuthContext);
