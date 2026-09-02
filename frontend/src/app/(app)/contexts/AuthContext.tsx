'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { api, clearTokens, getAccessToken, setTokens } from '../lib/api';
import { AuthResponse, User } from '../types';

interface AuthCtx {
  user: User | null;
  loading: boolean;
  login: (phone: string, password: string) => Promise<void>;
  register: (payload: any) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMe = async () => {
    try {
      const { data } = await api.get<User>('/auth/me/');
      setUser(data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (getAccessToken()) fetchMe();
    else setLoading(false);
  }, []);

  const login = async (phone_number: string, password: string) => {
    const { data } = await api.post<AuthResponse>('/auth/login/', { phone_number, password });
    setTokens(data.access, data.refresh);
    setUser(data.user);
  };

  const register = async (payload: any) => {
    const { data } = await api.post<AuthResponse>('/auth/register/', payload);
    setTokens(data.access, data.refresh);
    setUser(data.user);
  };

  const logout = () => {
    clearTokens();
    setUser(null);
    if (typeof window !== 'undefined') window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refresh: fetchMe }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
