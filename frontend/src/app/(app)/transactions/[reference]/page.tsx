'use client';

import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Loader2, Share2, Download, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { api } from '../../../lib/api';
import { formatNaira, formatDate, statusBadgeClass, networkLogo, cn } from '../../../lib/utils';
import { Transaction } from '../../../types';

export default function TransactionDetailPage({ params }: { params: { reference: string } }) {
  const { reference } = params;

  const { data: tx, isLoading } = useQuery<Transaction>({
    queryKey: ['transaction', reference],
    queryFn: async () => (await api.get(`/transactions/${reference}/`)).data,
    refetchInterval: (query) => {
      const s = query.state.data?.status;
      return s === 'processing' || s === 'pending' ? 2000 : false;
    },
  });

  const share = () => {
    if (!tx) return;
    const text = `BRAM Transaction Receipt\n${tx.variation_name}\nRecipient: ${tx.recipient}\nAmount: ${formatNaira(tx.sale_price)}\nStatus: ${tx.status.toUpperCase()}\nRef: ${tx.reference}`;
    if (navigator.share) {
      navigator.share({ title: 'BRAM Receipt', text });
    } else {
      navigator.clipboard.writeText(text);
      toast.success('Receipt copied');
    }
  };

  if (isLoading) return (
    <div className="flex items-center justify-center py-24">
      <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
    </div>
  );

  if (!tx) return (
    <div className="text-center text-surface-500 py-16">Transaction not found</div>
  );

  const logo = networkLogo(tx.network);
  const StatusIcon = tx.status === 'success' ? CheckCircle2
    : tx.status === 'failed' ? XCircle
    : Clock;
  const statusIconColor = tx.status === 'success' ? 'text-primary-600'
    : tx.status === 'failed' ? 'text-danger'
    : 'text-gold-600';

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <Link href="/transactions" className="inline-flex items-center gap-1 text-sm text-surface-600 hover:text-surface-900 dark:text-surface-400">
        <ArrowLeft className="h-4 w-4" /> Back
      </Link>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-elevated relative overflow-hidden"
      >
        {/* Ticket edge effect */}
        <div className="absolute inset-x-6 top-1/2 -translate-y-1/2">
          <div className="border-t-2 border-dashed border-surface-200 dark:border-surface-800" />
        </div>
        <div className="absolute -left-3 top-1/2 h-6 w-6 -translate-y-1/2 rounded-full bg-surface-50 dark:bg-surface-950" />
        <div className="absolute -right-3 top-1/2 h-6 w-6 -translate-y-1/2 rounded-full bg-surface-50 dark:bg-surface-950" />

        <div className="relative pb-8">
          <div className="text-center">
            <StatusIcon className={cn('mx-auto h-14 w-14', statusIconColor)} />
            <div className="mt-3">
              <span className={statusBadgeClass(tx.status)}>{tx.status.toUpperCase()}</span>
            </div>
            <div className="mt-4 text-4xl font-bold">{formatNaira(tx.sale_price)}</div>
            <div className="mt-1 flex items-center justify-center gap-2 text-surface-600 dark:text-surface-400">
              <div className={cn('flex h-6 w-6 items-center justify-center rounded text-[10px] font-bold', logo.bg, logo.text)}>
                {logo.short}
              </div>
              <span>{tx.variation_name}</span>
            </div>
          </div>
        </div>

        <div className="relative pt-8 space-y-3 text-sm">
          <Row label="Reference" value={<span className="font-mono text-xs">{tx.reference}</span>} />
          <Row label="Recipient" value={<span className="font-mono">{tx.recipient}</span>} />
          <Row label="Network" value={<span className="uppercase">{tx.network}</span>} />
          <Row label="Type" value={<span className="capitalize">{tx.transaction_type.replace('_', ' ')}</span>} />
          <Row label="Amount" value={formatNaira(tx.amount)} />
          <Row label="Date" value={formatDate(tx.created_at)} />
          {tx.completed_at && <Row label="Completed" value={formatDate(tx.completed_at)} />}
          {tx.status_message && (
            <Row label="Note" value={<span className="text-right">{tx.status_message}</span>} />
          )}
        </div>

        {(tx.status === 'processing' || tx.status === 'pending') && (
          <div className="mt-6 rounded-xl bg-gold-50 p-3 text-center text-xs text-gold-800 dark:bg-gold-950/30 dark:text-gold-300">
            <Loader2 className="mx-auto mb-1 h-4 w-4 animate-spin" />
            Processing your transaction — this page will update automatically
          </div>
        )}
      </motion.div>

      <div className="grid grid-cols-2 gap-3">
        <button onClick={share} className="btn-secondary">
          <Share2 className="h-4 w-4" /> Share
        </button>
        <Link href={`/buy/${tx.transaction_type}`} className="btn-primary">
          Buy again
        </Link>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-4">
      <span className="text-surface-500">{label}</span>
      <span className="font-medium text-right max-w-[65%] break-words">{value}</span>
    </div>
  );
}
