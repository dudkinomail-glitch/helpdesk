import axios from 'axios';
import { apiBaseUrl } from '../lib/runtimeConfig';

export const api = axios.create({
  baseURL: apiBaseUrl(),
});

api.interceptors.request.use((cfg) => {
  const t = localStorage.getItem('access_token');
  if (t) {
    cfg.headers.Authorization = `Bearer ${t}`;
  }
  return cfg;
});
