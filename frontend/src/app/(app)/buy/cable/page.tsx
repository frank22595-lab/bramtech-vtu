'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Loader2, Tv, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { api } from '../../../../lib/api';
import { formatNaira, generateIdempotencyKey, networkLogo, cn } from '../../../../lib/utils';
import { Service, ServiceVariation } from '../../../../types';

export default function BuyCablePage() {
  const router = useRouter();
  const [provider, setProvider] = useState('');
  const [smartcard, setSmartcard] = useState('');
  const [selectedVariation, setSelectedVariation] = useState('');
  const [pin, setPin] = useState('');

  const { data: services = [] } = useQuery<Service[]>({
    queryKey: ['services', 'cable_tv'],
    queryFn: async () => (await api.get('/services/?category=cable_tv')).data,
  });

  const currentService = services.find((s) => s.network === provider);

  const { data: variations = [] } = useQuery<ServiceVariation[]>({
    queryKey: ['variations', currentService?.slug],
    queryFn: async () => (await api.get(`/services/${currentService?.slug}/variations/`)).data,
    enabled: !!currentService,
  });

  const purchase = useMutation({
    mutationFn: async () => (await api.post('/purchase/', {
      variation_id: selectedVariation,
      recipient: smartcard,
      pin,
      idempotency_key: generateIdempotencyKey(),
    })).data,
    onSuccess: (data) => {
      toast.success('Subscription submitted');
      router.push(`/transactions/${data.reference}`);
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || 'Purchase failed'),
  });

  const canBuy = provider && smartcard.length >= 8 && selectedVariation && pin.length >= 4;

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <Link href="/dashboard" className="inline-flex items-center gap-1 text-sm text-surface-600 hover:text-surface-900 dark:text-surface-400">
        <ArrowLeft className="h-4 w-4" /> Back
      </Link>

      <div>
        <h1 className="text-display-sm flex items-center gap-2">
          <Tv className="h-7 w-7 text-primary-700" /> Cable TV
        </h1>
        <p className="mt-1 text-surface-600 dark:text-surface-400">DStv, GOtv, StarTimes</p>
      </div>

      <div className="card-elevated space-y-5">
        <div>
          <label className="label">Provider</label>
          <div className="grid grid-cols-3 gap-2">
            {services.map((s) => {
              const logo = networkLogo(s.network);
              return (
                <button
                  key={s.public_id}
                  type="button"
                  onClick={() => { setProvider(s.network); setSelectedVariation(''); }}
                  className={cn(
                    'rounded-xl border-2 p-3 transition',
                    provider === s.network
                      ? 'border-primary-600 bg-primary-50 dark:bg-primary-950/30'
                      : 'border-surface-200 hover:border-surface-300 dark:border-surface-800'
                  )}
                >
                  <div className={cn('mx-auto flex h-9 w-9 items-center justify-center rounded-lg text-[10px] font-bold', logo.bg, logo.text)}>
                    {logo.short}
                  </div>
                  <div className="mt-1 text-xs font-medium">{s.name}</div>
                </button>
              );
            })}
            {!services.length && <div className="col-span-3 text-center text-xs text-surface-500">Loading...</div>}
          </div>
        </div>

        <div>
          <label className="label">Smartcard / IUC number</label>
          <input
            type="text"
            placeholder="10-digit number"
            value={smartcard}
            onChange={(e) => setSmartcard(e.target.value)}
            className="input font-mono"
          />
        </div>

        {provider && (
          <div>
            <label className="label">Package</label>
            <div className="space-y-2">
              {variations.map((v) => (
                <button
                  key={v.public_id}
                  type="button"
                  onClick={() => setSelectedVariation(v.public_id)}
                  className={cn(
                    'flex w-full items-center justify-between rounded-2xl border-2 p-4 text-left transition',
                    selectedVariation === v.public_id
                      ? 'border-primary-600 bg-primary-50 dark:bg-primary-950/30'
                      : 'border-surface-200 hover:border-surface-300 dark:border-surface-800'
                  )}
                >
                  <div>
                    <div className="font-semibold">{v.name}</div>
                    <div className="text-xs text-surface-500">30 days</div>
                  </div>
                  <div className="font-bold text-primary-700 dark:text-primary-400">{v.price ? formatNaira(v.price) : '—'}</div>
                </button>
              ))}
            </div>
          </div>
        )}

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
          {purchase.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Subscribe'}
        </button>
      </div>
    </div>
  );
}
