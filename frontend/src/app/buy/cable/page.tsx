'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, formatNaira, getAccessToken } from '../../api-client';

export default function BuyCablePage() {
  const router = useRouter();
  const [services, setServices] = useState<any[]>([]);
  const [variations, setVariations] = useState<any[]>([]);
  const [provider, setProvider] = useState('');
  const [card, setCard] = useState('');
  const [variationId, setVariationId] = useState('');
  const [pin, setPin] = useState('');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    if (!getAccessToken()) { router.push('/auth/login'); return; }
    api.get('/services/?category=cable_tv').then((r) => setServices(r.data));
  }, [router]);

  useEffect(() => {
    const s = services.find((x) => x.network === provider);
    if (!s) return;
    api.get(`/services/${s.slug}/variations/`).then((r) => setVariations(r.data));
    setVariationId('');
  }, [provider, services]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg('');
    setLoading(true);
    try {
      const { data } = await api.post('/purchase/', {
        variation_id: variationId,
        recipient: card,
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
          <h1 className="font-bold">Cable TV</h1>
          <div className="w-12"></div>
        </div>
      </nav>
      <main className="max-w-lg mx-auto p-4">
        <div className="card">
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="label">Provider</label>
              <div className="grid grid-cols-3 gap-2">
                {services.map((s) => (
                  <button key={s.public_id} type="button" onClick={() => setProvider(s.network)}
                    className={`p-3 rounded-lg border-2 text-xs font-bold ${provider === s.network ? 'border-brand-700 bg-brand-50' : 'border-gray-200'}`}>
                    {s.name}
                  </button>
                ))}
                {!services.length && <div className="col-span-3 text-xs text-gray-500 p-4 text-center">Loading...</div>}
              </div>
            </div>
            <div>
              <label className="label">Smartcard / IUC number</label>
              <input type="text" value={card} onChange={(e) => setCard(e.target.value)} className="input font-mono" required />
            </div>
            {provider && (
              <div>
                <label className="label">Package</label>
                <div className="space-y-2">
                  {variations.map((v) => (
                    <button key={v.public_id} type="button" onClick={() => setVariationId(v.public_id)}
                      className={`w-full flex justify-between p-3 rounded-lg border-2 text-left ${variationId === v.public_id ? 'border-brand-700 bg-brand-50' : 'border-gray-200'}`}>
                      <span className="font-semibold text-sm">{v.name}</span>
                      <span className="font-bold text-brand-700">{v.price ? formatNaira(v.price) : '—'}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
            <div>
              <label className="label">PIN</label>
              <input type="password" inputMode="numeric" value={pin} onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))} className="input text-center tracking-widest" maxLength={6} placeholder="••••" required minLength={4} />
            </div>
            {msg && <p className="text-red-600 text-sm">{msg}</p>}
            <button type="submit" disabled={loading || !variationId} className="btn btn-primary btn-lg w-full">
              {loading ? 'Sending...' : 'Subscribe'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
