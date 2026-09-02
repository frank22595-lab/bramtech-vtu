'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Loader2, Zap, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { api } from '../../../../lib/api';
import { generateIdempotencyKey, cn } from '../../../../lib/utils';
import { Service, ServiceVariation } from '../../../../types';

export default function BuyElectricityPage() {
  const router = useRouter();
  const [disco, setDisco] = useState('');
  const [meter, setMeter] = useState('');
  const [meterType, setMeterType] = useState<'prepaid' | 'postpaid'>('prepaid');
  const [amount, setAmount] = useState<number | ''>('');
  const [pin, setPin] = useState('');

  const { data: services = [] } = useQuery<Service[]>({
    queryKey: ['services', 'electricity'],
    queryFn: async () => (await api.get('/services/?category=electricity')).data,
  });

  const currentService = services.find((s) => s.network === disco);

  const { data: variations = [] } = useQuery<ServiceVariation[]>({
    queryKey: ['variations', currentService?.slug],
    queryFn: async () => (await api.get(`/services/${currentService?.slug}/variations/`)).data,
    enabled: !!currentService,
  });

  const purchase = useMutation({
    mutationFn: async () => {
      const variation = variations[0];
      if (!variation) throw new Error('No variation');
      return (await api.post('/purchase/', {
        variation_id: variation.public_id,
        recipient: meter,
        amount: Number(amount),
        pin,
        idempotency_key: generateIdempotencyKey(),
        recipient_meta: { meter_type: meterType },
      })).data;
    },
    onSuccess: (data) => {
      toast.success('Payment submitted');
      router.push(`/transactions/${data.reference}`);
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || 'Purchase failed'),
  });

  const canBuy = disco && meter.length >= 8 && amount && Number(amount) >= 100 && pin.length >= 4;

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <Link href="/dashboard" className="inline-flex items-center gap-1 text-sm text-surface-600 hover:text-surface-900 dark:text-surface-400">
        <ArrowLeft className="h-4 w-4" /> Back
      </Link>

      <div>
        <h1 className="text-display-sm flex items-center gap-2">
          <Zap className="h-7 w-7 text-gold-600" /> Electricity
        </h1>
        <p className="mt-1 text-surface-600 dark:text-surface-400">Buy tokens for prepaid & postpaid</p>
      </div>

      <div className="card-elevated space-y-5">
        <div>
          <label className="label">DisCo</label>
          <div className="grid grid-cols-3 gap-2">
            {services.map((s) => (
              <button
                key={s.public_id}
                type="button"
                onClick={() => setDisco(s.network)}
                className={cn(
                  'rounded-xl border-2 p-3 text-xs font-semibold uppercase transition',
                  disco === s.network
                    ? 'border-primary-600 bg-primary-50 text-primary-700 dark:bg-primary-950/30'
                    : 'border-surface-200 hover:border-surface-300 dark:border-surface-800'
                )}
              >
                {s.name}
              </button>
            ))}
            {!services.length && (
              <div className="col-span-3 text-center text-xs text-surface-500 p-4 border-2 border-dashed rounded-xl">
                Configure electricity services in the admin panel first
              </div>
            )}
          </div>
        </div>

        <div>
          <label className="label">Meter type</label>
          <div className="grid grid-cols-2 gap-2">
            {(['prepaid', 'postpaid'] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setMeterType(t)}
                className={cn(
                  'rounded-xl border-2 p-3 text-sm font-semibold capitalize transition',
                  meterType === t
                    ? 'border-primary-600 bg-primary-50 text-primary-700 dark:bg-primary-950/30'
                    : 'border-surface-200 hover:border-surface-300 dark:border-surface-800'
                )}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="label">Meter number</label>
          <input
            type="text"
            placeholder="Meter number"
            value={meter}
            onChange={(e) => setMeter(e.target.value)}
            className="input font-mono"
          />
        </div>

        <div>
          <label className="label">Amount (₦)</label>
          <input
            type="number"
            placeholder="Minimum ₦100"
            value={amount}
            onChange={(e) => setAmount(e.target.value ? Number(e.target.value) : '')}
            className="input text-lg font-semibold"
            min={100}
          />
        </div>

        <div>
          <label className="label">Transaction PIN</label>
          <input
            type="password"
            inputMode="numeric"
            placeholder="••••"
            value={pin}
            onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))}
            className="input text-center tracking-[0.5em] text-lg"
            maxLength={6}
          />
        </div>

        <button
          onClick={() => purchase.mutate()}
          disabled={!canBuy || purchase.isPending}
          className="btn-primary btn-lg w-full"
        >
          {purchase.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Pay Bill'}
        </button>
      </div>
    </div>
  );
}
