'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, getAccessToken } from '../../api-client';

export default function BuyElectricityPage() {
  const router = useRouter();
  const [services, setServices] = useState<any[]>([]);
  const [disco, setDisco] = useState('');
  const [meter, setMeter] = useState('');
  const [meterType, setMeterType] = useState<'prepaid' | 'postpaid'>('prepaid');
  const [amount, setAmount] = useState('');
  const [pin, setPin] = useState('');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    if (!getAccessToken()) { router.push('/auth/login'); return; }
    api.get('/services/?category=electricity').then((r) => setServices(r.data));
  }, [router]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg('');
    setLoading(true);
    try {
      const service = services.find((s) => s.network === disco);
      if (!service) throw new Error('Select DisCo');
      const vars = (await api.get(`/services/${service.slug}/variations/`)).data;
      if (!vars[0]) throw new Error('No variation');
      const { data } = await api.post('/purchase/', {
        variation_id: vars[0].public_id,
        recipient: meter,
        amount: Number(amount),
        pin,
        idempotency_key: `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`,
        recipient_meta: { meter_type: meterType },
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
          <h1 className="font-bold">Electricity</h1>
          <div className="w-12"></div>
        </div>
      </nav>
      <main className="max-w-lg mx-auto p-4">
        <div className="card">
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="label">DisCo</label>
              <div className="grid grid-cols-3 gap-2">
                {services.map((s) => (
                  <button key={s.public_id} type="button" onClick={() => setDisco(s.network)}
                    className={`p-3 rounded-lg border-2 text-xs font-bold uppercase ${disco === s.network ? 'border-brand-700 bg-brand-50' : 'border-gray-200'}`}>
                    {s.name}
                  </button>
                ))}
                {!services.length && <div className="col-span-3 text-xs text-gray-500 p-4 text-center border-2 border-dashed rounded-lg">No DisCos configured yet — add them in admin</div>}
              </div>
            </div>
            <div>
              <label className="label">Meter type</label>
              <div className="grid grid-cols-2 gap-2">
                {(['prepaid', 'postpaid'] as const).map((t) => (
                  <button key={t} type="button" onClick={() => setMeterType(t)}
                    className={`p-3 rounded-lg border-2 text-sm font-semibold capitalize ${meterType === t ? 'border-brand-700 bg-brand-50' : 'border-gray-200'}`}>
                    {t}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="label">Meter number</label>
              <input type="text" value={meter} onChange={(e) => setMeter(e.target.value)} className="input font-mono" required />
            </div>
            <div>
              <label className="label">Amount (₦)</label>
              <input type="number" value={amount} onChange={(e) => setAmount(e.target.value)} className="input" placeholder="Min ₦100" min={100} required />
            </div>
            <div>
              <label className="label">PIN</label>
              <input type="password" inputMode="numeric" value={pin} onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))} className="input text-center tracking-widest" maxLength={6} placeholder="••••" required minLength={4} />
            </div>
            {msg && <p className="text-red-600 text-sm">{msg}</p>}
            <button type="submit" disabled={loading} className="btn btn-primary btn-lg w-full">
              {loading ? 'Sending...' : 'Pay Bill'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
