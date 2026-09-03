'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, formatNaira, getAccessToken } from '../../api-client';

export default function BuyDataPage() {
  const router = useRouter();
  const [services, setServices] = useState<any[]>([]);
  const [variations, setVariations] = useState<any[]>([]);
  const [network, setNetwork] = useState('');
  const [phone, setPhone] = useState('');
  const [variationId, setVariationId] = useState('');
  const [pin, setPin] = useState('');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    if (!getAccessToken()) { router.push('/auth/login'); return; }
    api.get('/services/?category=data').then((r) => setServices(r.data));
  }, [router]);

  useEffect(() => {
    const service = services.find((s) => s.network === network);
    if (!service) return;
    api.get(`/services/${service.slug}/variations/`).then((r) => setVariations(r.data));
    setVariationId('');
  }, [network, services]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg('');
    setLoading(true);
    try {
      const { data } = await api.post('/purchase/', {
        variation_id: variationId,
        recipient: phone,
        pin,
        idempotency_key: `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`,
      });
      router.push(`/transactions?ref=${data.reference}`);
    } catch (err: any) {
      setMsg(err?.response?.data?.detail || 'Purchase failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b p-4">
        <div className="max-w-lg mx-auto flex justify-between">
          <Link href="/dashboard" className="text-sm">← Back</Link>
          <h1 className="font-bold">Buy Data</h1>
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
                  <button key={s.public_id} type="button" onClick={() => setNetwork(s.network)}
                    className={`p-3 rounded-lg border-2 text-xs font-bold uppercase ${network === s.network ? 'border-brand-700 bg-brand-50 text-brand-700' : 'border-gray-200'}`}>
                    {s.network}
                  </button>
                ))}
                {!services.length && <div className="col-span-4 text-xs text-gray-500 p-4 text-center">Loading...</div>}
              </div>
            </div>
            <div>
              <label className="label">Phone number</label>
              <input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} className="input" placeholder="08012345678" required />
            </div>
            {network && (
              <div>
                <label className="label">Plan</label>
                <div className="space-y-2">
                  {variations.map((v) => (
                    <button key={v.public_id} type="button" onClick={() => setVariationId(v.public_id)}
                      className={`w-full flex justify-between items-center p-3 rounded-lg border-2 text-left ${variationId === v.public_id ? 'border-brand-700 bg-brand-50' : 'border-gray-200'}`}>
                      <div>
                        <div className="font-semibold text-sm">{v.name}</div>
                        {v.validity_days && <div className="text-xs text-gray-500">{v.validity_days} days</div>}
                      </div>
                      <div className="font-bold text-brand-700">{v.price ? formatNaira(v.price) : '—'}</div>
                    </button>
                  ))}
                  {!variations.length && <div className="text-xs text-gray-500">No plans available</div>}
                </div>
              </div>
            )}
            <div>
              <label className="label">PIN</label>
              <input type="password" inputMode="numeric" value={pin} onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))} className="input text-center tracking-widest" maxLength={6} placeholder="••••" required minLength={4} />
            </div>
            {msg && <p className="text-red-600 text-sm">{msg}</p>}
            <button type="submit" disabled={loading || !variationId} className="btn btn-primary btn-lg w-full">
              {loading ? 'Sending...' : 'Buy Data'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
