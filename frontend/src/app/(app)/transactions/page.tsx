'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { Loader2, ShoppingBag } from 'lucide-react';
import { api } from '../../../lib/api';
import { formatNaira, statusBadgeClass, timeAgo, networkLogo, cn } from '../../../lib/utils';
import { Transaction } from '../../../types';

const STATUSES = ['all', 'processing', 'success', 'failed', 'refunded'];

export default function TransactionsPage() {
  const [status, setStatus] = useState('all');

  const { data, isLoading } = useQuery<{ count: number; results: Transaction[] }>({
    queryKey: ['transactions', status],
    queryFn: async () => {
      const params = status !== 'all' ? `?status=${status}` : '';
      return (await api.get(`/transactions/${params}`)).data;
    },
  });

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-display-sm">Transactions</h1>
        <p className="mt-1 text-surface-600 dark:text-surface-400">Complete history of your purchases</p>
      </div>

      <div className="no-scrollbar flex gap-2 overflow-x-auto">
        {STATUSES.map((s) => (
          <button
            key={s}
            onClick={() => setStatus(s)}
            className={cn(
              'whitespace-nowrap rounded-full border-2 px-4 py-1.5 text-xs font-semibold capitalize transition',
              status === s
                ? 'border-primary-600 bg-primary-600 text-white'
                : 'border-surface-200 bg-white text-surface-700 hover:border-surface-300 dark:border-surface-800 dark:bg-surface-900 dark:text-surface-300'
            )}
          >
            {s}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
        </div>
      ) : !data?.results?.length ? (
        <div className="card text-center py-16">
          <ShoppingBag className="mx-auto mb-3 h-10 w-10 text-surface-300" />
          <div className="font-semibold">No transactions</div>
          <div className="mt-1 text-sm text-surface-500">Purchases will appear here</div>
        </div>
      ) : (
        <div className="card divide-y divide-surface-100 dark:divide-surface-800">
          {data.results.map((t) => {
            const logo = networkLogo(t.network);
            return (
              <Link
                key={t.public_id}
                href={`/transactions/${t.reference}`}
                className="flex items-center gap-3 py-3 first:pt-0 last:pb-0 -mx-6 px-6 hover:bg-surface-50 dark:hover:bg-surface-900/50 first:rounded-t-2xl last:rounded-b-2xl"
              >
                <div className={cn('flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-xs font-bold', logo.bg, logo.text)}>
                  {logo.short}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="truncate font-semibold text-sm">{t.variation_name}</div>
                  <div className="text-xs text-surface-500">
                    {t.recipient} · {timeAgo(t.created_at)}
                  </div>
                  <div className="mt-0.5 font-mono text-[10px] text-surface-400">{t.reference}</div>
                </div>
                <div className="text-right">
                  <div className="font-bold">{formatNaira(t.sale_price)}</div>
                  <span className={statusBadgeClass(t.status)}>{t.status}</span>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
