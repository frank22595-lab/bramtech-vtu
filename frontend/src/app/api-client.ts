'use client';

import axios from 'axios';
import Cookies from 'js-cookie';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://bramtech-api.onrender.com/api/v1';

export const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = Cookies.get('bram_access');
  if (token && config.headers) {
    (config.headers as any).Authorization = `Bearer ${token}`;
  }
  return config;
});

export function setTokens(access: string, refresh: string) {
  Cookies.set('bram_access', access, { sameSite: 'lax', expires: 1 });
  Cookies.set('bram_refresh', refresh, { sameSite: 'lax', expires: 14 });
}

export function clearTokens() {
  Cookies.remove('bram_access');
  Cookies.remove('bram_refresh');
}

export function getAccessToken() {
  if (typeof window === 'undefined') return undefined;
  return Cookies.get('bram_access');
}

export function formatNaira(n: number | string | null | undefined) {
  if (n == null) return '₦0';
  const num = typeof n === 'string' ? parseFloat(n) : n;
  if (isNaN(num)) return '₦0';
  return '₦' + num.toLocaleString('en-NG', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
