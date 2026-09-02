'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Loader2, Wifi, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { api } from '../helpers';
import { formatNaira, generateIdempotencyKey, networkLogo, cn } from '../helpers';
import { Service, ServiceVariation } from '../helpers';

export default function BuyDataPage() {
  const router = useRouter();
  const [network, setNetwork] = useState<string>('');
  const [phone, setPhone] = useState('');
  const [selectedVariation, setSelectedVariation] = useState<string>('');
  const [pin, setPin] = useState('');

  const { data: services = [] } = useQuery<Service[]>({
    queryKey: ['services', 'data'],
    queryFn: async () => (await api.get('/services/?category=data')).data,
  });

  const currentService = services.find((s) => s.network === network);

  const { data: variations = [] } = useQuery<ServiceVariation[]>({
    queryKey: ['variations', currentService?.slug],
    queryFn: async () => (await api.get(`/services/${currentService?.slug}/variations/`)).data,
    enabled: !!currentService,
  });

  const purchase = useMutation({
    mutationFn: async () => (await api.post('/purchase/', {
      variation_id: selectedVariation,
      recipient: phone,
      pin,
      idempotency_key: generateIdempotencyKey(),
    })).data,
    onSuccess: (data) => {
      toast.success('Data submitted');
      router.push(`/transactions/${data.reference}`);
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || 'Purchase failed'),
  });

  const canBuy = network && phone.length >= 10 && selectedVariation && pin.length >= 4;

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <Link href="/dashboard" className="inline-flex items-center gap-1 text-sm text-surface-600 hover:text-surface-900 dark:text-surface-400">
        <ArrowLeft className="h-4 w-4" /> Back
      </Link>

      <div>
        <h1 className="text-display-sm flex items-center gap-2">
          <Wifi className="h-7 w-7 text-primary-700" /> Buy Data
        </h1>
        <p className="mt-1 text-surface-600 dark:text-surface-400">Data bundles for any network</p>
      </div>

      <div className="card-elevated space-y-5">
        <div>
          <label className="label">Network</label>
          <div className="grid grid-cols-4 gap-2">
            {services.map((s) => {
              const logo = networkLogo(s.network);
              return (
                <button
                  key={s.public_id}
                  type="button"
                  onClick={() => { setNetwork(s.network); setSelectedVariation(''); }}
                  className={cn(
                    'rounded-xl border-2 p-3 transition',
                    network === s.network
                      ? 'border-primary-600 bg-primary-50 dark:bg-primary-950/30'
                      : 'border-surface-200 hover:border-surface-300 dark:border-surface-800'
                  )}
                >
                  <div className={cn('mx-auto flex h-8 w-8 items-center justify-center rounded-lg text-[10px] font-bold', logo.bg, logo.text)}>
                    {logo.short}
                  </div>
                </button>
              );
            })}
            {!services.length && <div className="col-span-4 text-center text-xs text-surface-500">Loading...</div>}
          </div>
        </div>

        <div>
          <label className="label">Phone number</label>
          <input
            type="tel"
            placeholder="08012345678"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            className="input text-lg font-mono"
            maxLength={14}
          />
        </div>

        {network && (
          <div>
            <label className="label">Choose a plan</label>
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
                    {v.validity_days && (
                      <div className="text-xs text-surface-500">{v.validity_days} days validity</div>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-primary-700 dark:text-primary-400">{v.price ? formatNaira(v.price) : '—'}</div>
                    {v.data_mb && (
                      <div className="text-xs text-surface-500">{(v.data_mb / 1024).toFixed(1)} GB</div>
                    )}
                  </div>
                </button>
              ))}
              {network && !variations.length && (
                <div className="text-sm text-surface-500">No plans available</div>
              )}
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
          {purchase.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Buy Data'}
        </button>
      </div>
    </div>
  );
}
