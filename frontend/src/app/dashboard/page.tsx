'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, clearTokens, formatNaira, getAccessToken } from '../api-client';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!getAccessToken()) {
      router.push('/auth/login');
      return;
    }
    api.get('/auth/me/').then((r) => {
      setUser(r.data);
      setLoading(false);
    }).catch(() => {
      clearTokens();
      router.push('/auth/login');
    });
  }, [router]);

  const logout = () => {
    clearTokens();
    router.push('/');
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-lg bg-brand-700 flex items-center justify-center text-white font-bold">B</div>
            <span className="font-bold text-xl">BRAM<span className="text-gold-500">.</span></span>
          </Link>
          <button onClick={logout} className="btn btn-outline">Sign out</button>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto p-4 py-8 space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Hello, {user?.first_name || 'there'} 👋</h1>
          <p className="text-gray-600">What would you like to buy today?</p>
        </div>

        {/* Wallet */}
        <div className="rounded-2xl bg-gradient-to-br from-brand-700 to-brand-900 text-white p-6">
          <div className="text-xs uppercase opacity-80">Wallet Balance</div>
          <div className="text-4xl font-bold mt-2">{formatNaira(user?.wallet_balance)}</div>
          <div className="mt-4 flex gap-2">
            <Link href="/wallet" className="px-4 py-2 rounded-lg bg-white/15 text-sm font-semibold hover:bg-white/25">
              Fund wallet
            </Link>
            <Link href="/transactions" className="px-4 py-2 rounded-lg bg-white/15 text-sm font-semibold hover:bg-white/25">
              History
            </Link>
          </div>
        </div>

        {/* Quick buy */}
        <div>
          <h2 className="text-lg font-bold mb-3">Quick Buy</h2>
          <div className="grid grid-cols-4 gap-3">
            {[
              { href: '/buy/airtime', label: 'Airtime', emoji: '📱' },
              { href: '/buy/data', label: 'Data', emoji: '📶' },
              { href: '/buy/cable', label: 'Cable', emoji: '📺' },
              { href: '/buy/electricity', label: 'Electric', emoji: '⚡' },
            ].map((q) => (
              <Link key={q.href} href={q.href} className="card text-center hover:shadow-lg transition">
                <div className="text-3xl mb-1">{q.emoji}</div>
                <div className="text-xs font-semibold">{q.label}</div>
              </Link>
            ))}
          </div>
        </div>

        {/* Info card */}
        <div className="card">
          <h3 className="font-bold mb-2">Account Info</h3>
          <div className="text-sm space-y-1 text-gray-700">
            <div><strong>Phone:</strong> {user?.phone_number}</div>
            <div><strong>Tier:</strong> {user?.tier}</div>
            <div><strong>Referral Code:</strong> <code className="bg-gray-100 px-2 py-0.5 rounded">{user?.referral_code}</code></div>
          </div>
        </div>
      </main>
    </div>
  );
}
