'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, getAccessToken } from '../../api-client';

export default function BuyAirtimePage() {
  const router = useRouter();
  const [services, setServices] = useState<any[]>([]);
  const [network, setNetwork] = useState('');
  const [phone, setPhone] = useState('');
  const [amount, setAmount] = useState('');
  const [pin, setPin] = useState('');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    if (!getAccessToken()) { router.push('/auth/login'); return; }
    api.get('/services/?category=airtime').then((r) => setServices(r.data));
  }, [router]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg('');
    setLoading(true);
    try {
      const service = services.find((s) => s.network === network);
      if (!service) throw new Error('Select a network');
      const variations = (await api.get(`/services/${service.slug}/variations/`)).data;
      if (!variations[0]) throw new Error('No variation');
      const { data } = await api.post('/purchase/', {
        variation_id: variations[0].public_id,
        recipient: phone,
        amount: Number(amount),
        pin,
        idempotency_key: `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`,
      });
      router.push(`/transactions?ref=${data.reference}`);
    } catch (err: any) {
      setMsg(err?.response?.data?.detail || err?.message || 'Purchase failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b p-4">
        <div className="max-w-lg mx-auto flex justify-between">
          <Link href="/dashboard" className="text-sm">← Back</Link>
          <h1 className="font-bold">Buy Airtime</h1>
          <div className="w-12"></div>
        </div>
      </nav>

      <main className="max-w-lg mx-auto p-4">
        <div className="card">
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="label">Network</label>
              <div className="grid grid-cols-4 gap-2">
                {services.map((s) => (
                  <button
                    key={s.public_id}
                    type="button"
                    onClick={() => setNetwork(s.network)}
                    className={`p-3 rounded-lg border-2 text-xs font-bold uppercase ${
                      network === s.network ? 'border-brand-700 bg-brand-50 text-brand-700' : 'border-gray-200'
                    }`}
                  >
                    {s.network}
                  </button>
                ))}
                {!services.length && <div className="col-span-4 text-center text-xs text-gray-500 py-4">Loading networks...</div>}
              </div>
            </div>
            <div>
              <label className="label">Phone number</label>
              <input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} className="input" placeholder="08012345678" required />
            </div>
            <div>
              <label className="label">Amount (₦)</label>
              <div className="grid grid-cols-3 gap-2 mb-2">
                {[100, 200, 500, 1000, 2000, 5000].map((a) => (
                  <button
                    key={a}
                    type="button"
                    onClick={() => setAmount(String(a))}
                    className={`py-2 rounded-lg border-2 text-sm font-bold ${amount === String(a) ? 'border-brand-700 bg-brand-50 text-brand-700' : 'border-gray-200'}`}
                  >₦{a}</button>
                ))}
              </div>
              <input type="number" value={amount} onChange={(e) => setAmount(e.target.value)} className="input" placeholder="Or custom amount" min={50} required />
            </div>
            <div>
              <label className="label">Transaction PIN</label>
              <input type="password" inputMode="numeric" value={pin} onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))} className="input text-center tracking-widest" maxLength={6} placeholder="••••" required minLength={4} />
            </div>
            {msg && <p className="text-red-600 text-sm">{msg}</p>}
            <button type="submit" disabled={loading} className="btn btn-primary btn-lg w-full">
              {loading ? 'Sending...' : `Send ₦${amount || '0'}`}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
