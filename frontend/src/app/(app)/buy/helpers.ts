import axios, { AxiosError, AxiosInstance } from 'axios';
import Cookies from 'js-cookie';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export const ACCESS_TOKEN_KEY = 'bram_access';
export const REFRESH_TOKEN_KEY = 'bram_refresh';

export function getAccessToken(): string | undefined {
  if (typeof window === 'undefined') return undefined;
  return Cookies.get(ACCESS_TOKEN_KEY);
}
export function getRefreshToken(): string | undefined {
  if (typeof window === 'undefined') return undefined;
  return Cookies.get(REFRESH_TOKEN_KEY);
}
export function setTokens(access: string, refresh: string) {
  Cookies.set(ACCESS_TOKEN_KEY, access, { sameSite: 'lax', expires: 1 });
  Cookies.set(REFRESH_TOKEN_KEY, refresh, { sameSite: 'lax', expires: 14 });
}
export function clearTokens() {
  Cookies.remove(ACCESS_TOKEN_KEY);
  Cookies.remove(REFRESH_TOKEN_KEY);
}

let isRefreshing = false;
let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refresh = getRefreshToken();
  if (!refresh) throw new Error('No refresh token');
  const { data } = await axios.post(`${API_BASE}/auth/refresh/`, { refresh });
  Cookies.set(ACCESS_TOKEN_KEY, data.access, { sameSite: 'lax', expires: 1 });
  return data.access;
}

export const api: AxiosInstance = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 20000,
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers = config.headers || {};
    (config.headers as any).Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as any;
    if (error.response?.status === 401 && !original._retry && original.url !== '/auth/refresh/') {
      original._retry = true;
      try {
        if (!isRefreshing) {
          isRefreshing = true;
          refreshPromise = refreshAccessToken().finally(() => {
            isRefreshing = false;
            refreshPromise = null;
          });
        }
        const newToken = await refreshPromise!;
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      } catch (e) {
        clearTokens();
        if (typeof window !== 'undefined') window.location.href = '/login';
        throw e;
      }
    }
    return Promise.reject(error);
  }
);


import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNaira(n: number | string | null | undefined, opts: { showSymbol?: boolean; decimals?: boolean } = {}) {
  const { showSymbol = true, decimals = true } = opts;
  if (n == null) return showSymbol ? '₦0' : '0';
  const num = typeof n === 'string' ? parseFloat(n) : n;
  if (isNaN(num)) return showSymbol ? '₦0' : '0';
  const formatted = num.toLocaleString('en-NG', {
    minimumFractionDigits: decimals ? 2 : 0,
    maximumFractionDigits: decimals ? 2 : 0,
  });
  return showSymbol ? `₦${formatted}` : formatted;
}

export function formatPhoneNG(v: string): string {
  const cleaned = v.replace(/[^\d+]/g, '');
  if (cleaned.startsWith('+234')) return cleaned;
  if (cleaned.startsWith('234')) return `+${cleaned}`;
  if (cleaned.startsWith('0')) return `+234${cleaned.substring(1)}`;
  return cleaned;
}

export function generateIdempotencyKey() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

export function formatDate(iso: string, opts: { time?: boolean } = { time: true }) {
  const d = new Date(iso);
  if (opts.time === false) {
    return d.toLocaleDateString('en-NG', { day: '2-digit', month: 'short', year: 'numeric' });
  }
  return d.toLocaleString('en-NG', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export function timeAgo(iso: string): string {
  const now = Date.now();
  const then = new Date(iso).getTime();
  const s = Math.floor((now - then) / 1000);
  if (s < 60) return 'just now';
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  if (s < 604800) return `${Math.floor(s / 86400)}d ago`;
  return formatDate(iso, { time: false });
}

export function statusBadgeClass(status: string): string {
  switch (status) {
    case 'success': return 'badge-success';
    case 'failed': return 'badge-danger';
    case 'processing':
    case 'pending': return 'badge-warning';
    case 'refunded': return 'badge-info';
    default: return 'badge-neutral';
  }
}

export function networkLogo(network: string): { bg: string; text: string; short: string } {
  const map: Record<string, { bg: string; text: string; short: string }> = {
    mtn:      { bg: 'bg-yellow-400', text: 'text-black', short: 'MTN' },
    glo:      { bg: 'bg-green-600', text: 'text-white', short: 'Glo' },
    airtel:   { bg: 'bg-red-600', text: 'text-white', short: 'Airtel' },
    '9mobile':{ bg: 'bg-green-500', text: 'text-white', short: '9m' },
    dstv:     { bg: 'bg-blue-900', text: 'text-white', short: 'DStv' },
    gotv:     { bg: 'bg-orange-500', text: 'text-white', short: 'GOtv' },
    startimes:{ bg: 'bg-red-500', text: 'text-white', short: 'ST' },
    showmax:  { bg: 'bg-purple-600', text: 'text-white', short: 'SM' },
  };
  return map[network.toLowerCase()] || { bg: 'bg-surface-600', text: 'text-white', short: network.slice(0, 3).toUpperCase() };
}


export interface User {
  public_id: string;
  phone_number: string;
  email: string | null;
  first_name: string;
  last_name: string;
  full_name: string;
  tier: 'regular' | 'bronze' | 'silver' | 'gold' | 'platinum';
  kyc_tier: 0 | 1 | 2 | 3;
  referral_code: string;
  phone_verified: boolean;
  email_verified: boolean;
  wallet_balance: string;
  date_joined: string;
}

export interface Wallet {
  public_id: string;
  balance: string;
  status: 'active' | 'frozen' | 'suspended';
  created_at: string;
}

export interface VirtualAccount {
  account_number: string;
  bank_name: string;
  account_name: string;
}

export interface Service {
  public_id: string;
  category: string;
  network: string;
  name: string;
  slug: string;
  description: string;
  display_order: number;
  icon: string;
}

export interface ServiceVariation {
  public_id: string;
  service_name: string;
  network: string;
  name: string;
  variation_type: 'fixed' | 'variable_amount';
  variation_code: string;
  face_value: string | null;
  validity_days: number | null;
  data_mb: number | null;
  display_order: number;
  price: string | null;
}

export interface Transaction {
  public_id: string;
  reference: string;
  transaction_type: string;
  variation_name: string;
  network: string;
  recipient: string;
  amount: string;
  sale_price: string;
  status: 'pending' | 'processing' | 'success' | 'failed' | 'refunded';
  status_message: string;
  created_at: string;
  completed_at: string | null;
}

export interface AuthResponse {
  user: User;
  access: string;
  refresh: string;
}


