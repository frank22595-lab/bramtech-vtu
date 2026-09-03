'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, getAccessToken } from '../api-client';

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [pin, setPin] = useState('');
  const [confirmPin, setConfirmPin] = useState('');
  const [msg, setMsg] = useState('');

  useEffect(() => {
    if (!getAccessToken()) { router.push('/auth/login'); return; }
    api.get('/auth/me/').then((r) => setUser(r.data));
  }, [router]);

  const setPinFn = async () => {
    if (pin !== confirmPin) { setMsg("PINs don't match"); return; }
    if (pin.length < 4) { setMsg('PIN too short'); return; }
    try {
      await api.post('/auth/set-pin/', { pin });
      setMsg('PIN updated');
      setPin(''); setConfirmPin('');
    } catch (e: any) {
      setMsg(e?.response?.data?.detail || 'Failed');
    }
  };

  if (!user) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b p-4">
        <div className="max-w-2xl mx-auto flex justify-between">
          <Link href="/dashboard" className="text-sm">← Back</Link>
          <h1 className="font-bold">Profile</h1>
          <div className="w-12"></div>
        </div>
      </nav>
      <main className="max-w-2xl mx-auto p-4 space-y-4">
        <div className="card">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-brand-700 text-white flex items-center justify-center text-2xl font-bold">
              {(user.first_name?.[0] || user.phone_number[0]).toUpperCase()}
            </div>
            <div>
              <div className="font-bold text-lg">{user.full_name || 'Add your name'}</div>
              <div className="text-gray-600 text-sm">{user.phone_number}</div>
              {user.email && <div className="text-xs text-gray-500">{user.email}</div>}
            </div>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-4 pt-4 border-t">
            <div>
              <div className="text-xs text-gray-500">Tier</div>
              <div className="font-bold capitalize">{user.tier}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Referral Code</div>
              <div className="font-bold font-mono">{user.referral_code}</div>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="font-bold mb-3">Transaction PIN</h2>
          <p className="text-sm text-gray-600 mb-3">4-6 digit PIN required for every purchase</p>
          <div className="space-y-3">
            <div>
              <label className="label">New PIN</label>
              <input type="password" inputMode="numeric" value={pin} onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))} className="input text-center tracking-widest" maxLength={6} placeholder="••••" />
            </div>
            <div>
              <label className="label">Confirm PIN</label>
              <input type="password" inputMode="numeric" value={confirmPin} onChange={(e) => setConfirmPin(e.target.value.replace(/\D/g, ''))} className="input text-center tracking-widest" maxLength={6} placeholder="••••" />
            </div>
            {msg && <p className="text-sm text-brand-700">{msg}</p>}
            <button onClick={setPinFn} disabled={pin.length < 4 || pin !== confirmPin} className="btn btn-primary w-full">
              Update PIN
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
