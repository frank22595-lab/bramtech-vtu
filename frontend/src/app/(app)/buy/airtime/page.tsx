'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Loader2, Phone, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { api } from '../../../../lib/api';
import { formatNaira, generateIdempotencyKey, networkLogo, cn } from '../../../../lib/utils';
import { Service, ServiceVariation } from '../../../../types';

const PRESET_AMOUNTS = [100, 200, 500, 1000, 2000, 5000];

export default function BuyAirtimePage() {
  const router = useRouter();
  const [network, setNetwork] = useState<string>('');
  const [phone, setPhone] = useState('');
  const [amount, setAmount] = useState<number | ''>('');
  const [pin, setPin] = useState('');

  const { data: services = [] } = useQuery<Service[]>({
    queryKey: ['services', 'airtime'],
    queryFn: async () => (await api.get('/services/?category=airtime')).data,
  });

  const currentService = services.find((s) => s.network === network);

  const { data: variations = [] } = useQuery<ServiceVariation[]>({
    queryKey: ['variations', currentService?.slug],
    queryFn: async () => (await api.get(`/services/${currentService?.slug}/variations/`)).data,
    enabled: !!currentService,
  });

  const variation = variations[0];

  const purchase = useMutation({
    mutationFn: async () => {
      if (!variation) throw new Error('No variation');
      return (await api.post('/purchase/', {
        variation_id: variation.public_id,
        recipient: phone,
        amount: Number(amount),
        pin,
        idempotency_key: generateIdempotencyKey(),
      })).data;
    },
    onSuccess: (data) => {
      toast.success('Airtime submitted');
      router.push(`/transactions/${data.reference}`);
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || 'Purchase failed'),
  });

  const canBuy = network && phone.length >= 10 && amount && Number(amount) >= 50 && pin.length >= 4;

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <Link href="/dashboard" className="inline-flex items-center gap-1 text-sm text-surface-600 hover:text-surface-900 dark:text-surface-400">
        <ArrowLeft className="h-4 w-4" /> Back
      </Link>

      <div>
        <h1 className="text-display-sm flex items-center gap-2">
          <Phone className="h-7 w-7 text-primary-700" /> Buy Airtime
        </h1>
        <p className="mt-1 text-surface-600 dark:text-surface-400">Recharge any Nigerian phone</p>
      </div>

      <div className="card-elevated space-y-5">
        {/* Network */}
        <div>
          <label className="label">Network</label>
          <div className="grid grid-cols-4 gap-2">
            {services.map((s) => {
              const logo = networkLogo(s.network);
              return (
                <button
                  key={s.public_id}
                  type="button"
                  onClick={() => setNetwork(s.network)}
                  className={cn(
                    'rounded-xl border-2 p-3 text-center transition',
                    network === s.network
                      ? 'border-primary-600 bg-primary-50 dark:bg-primary-950/30'
                      : 'border-surface-200 hover:border-surface-300 dark:border-surface-800'
                  )}
                >
                  <div className={cn('mx-auto mb-1 flex h-8 w-8 items-center justify-center rounded-lg text-[10px] font-bold', logo.bg, logo.text)}>
                    {logo.short}
                  </div>
                </button>
              );
            })}
            {!services.length && <div className="col-span-4 text-center text-xs text-surface-500">Loading...</div>}
          </div>
        </div>

        {/* Phone */}
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

        {/* Amount */}
        <div>
          <label className="label">Amount</label>
          <div className="mb-3 grid grid-cols-3 gap-2">
            {PRESET_AMOUNTS.map((a) => (
              <button
                key={a}
                type="button"
                onClick={() => setAmount(a)}
                className={cn(
                  'rounded-xl border-2 py-2.5 text-sm font-bold transition',
                  amount === a
                    ? 'border-primary-600 bg-primary-50 text-primary-700 dark:bg-primary-950/30 dark:text-primary-400'
                    : 'border-surface-200 hover:border-surface-300 dark:border-surface-800'
                )}
              >
                ₦{formatNaira(a, { showSymbol: false, decimals: false })}
              </button>
            ))}
          </div>
          <input
            type="number"
            placeholder="Or enter custom amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value ? Number(e.target.value) : '')}
            className="input"
            min={50}
            max={50000}
          />
        </div>

        {/* PIN */}
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
          {purchase.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <>Send {amount ? formatNaira(amount) : 'Airtime'}</>
          )}
        </button>
      </div>
    </div>
  );
}
