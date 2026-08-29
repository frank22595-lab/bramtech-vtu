'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Copy, Check, Wallet as WalletIcon, Building2, ArrowUp, Info, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { formatNaira } from '@/lib/utils';
import { VirtualAccount } from '@/types';

export default function WalletPage() {
  const { user } = useAuth();
  const [copied, setCopied] = useState<string | null>(null);

  const { data: accounts, isLoading } = useQuery<VirtualAccount[]>({
    queryKey: ['virtual-accounts'],
    queryFn: async () => (await api.get('/wallet/virtual-accounts/')).data,
  });

  const copy = (v: string, key: string) => {
    navigator.clipboard.writeText(v);
    setCopied(key);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopied(null), 1500);
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-display-sm">Wallet</h1>
        <p className="mt-1 text-surface-600 dark:text-surface-400">Fund by bank transfer, instant credit</p>
      </div>

      {/* Balance */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-700 via-primary-800 to-primary-950 p-8 text-white shadow-elevated"
      >
        <div className="absolute inset-0 bg-grid-pattern opacity-[0.04]" />
        <div className="relative">
          <div className="text-xs uppercase tracking-wider text-white/70">Available Balance</div>
          <div className="mt-2 text-5xl font-bold">{formatNaira(user?.wallet_balance ?? '0')}</div>
          <div className="mt-4 text-sm text-white/80">
            Wallet status: <span className="font-semibold capitalize">Active</span>
          </div>
        </div>
      </motion.div>

      {/* Virtual accounts */}
      <div className="card-elevated">
        <div className="mb-5 flex items-center gap-2">
          <Building2 className="h-5 w-5 text-primary-700" />
          <h2 className="text-lg font-bold">Your funding accounts</h2>
        </div>

        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-primary-600" />
          </div>
        )}

        {!isLoading && !accounts?.length && (
          <div className="rounded-2xl bg-gold-50 p-5 dark:bg-gold-950/20">
            <div className="flex gap-3">
              <Info className="h-5 w-5 shrink-0 text-gold-600" />
              <div>
                <div className="font-semibold text-surface-900 dark:text-surface-100">Virtual account coming soon</div>
                <p className="mt-1 text-sm text-surface-700 dark:text-surface-300">
                  We're finalizing our banking partnership. Until it's live, contact us on WhatsApp to fund your wallet manually.
                </p>
                <a
                  href="https://wa.me/2348137925907"
                  target="_blank"
                  rel="noreferrer"
                  className="btn-primary btn-sm mt-3"
                >
                  Contact support
                </a>
              </div>
            </div>
          </div>
        )}

        <div className="space-y-3">
          {accounts?.map((a) => (
            <div
              key={a.account_number}
              className="group rounded-2xl border border-surface-200 p-5 transition hover:border-primary-300 dark:border-surface-800"
            >
              <div className="mb-3 flex items-center justify-between">
                <div className="text-xs uppercase tracking-wider text-surface-500 font-semibold">
                  {a.bank_name}
                </div>
                <div className="badge-success">Active</div>
              </div>
              <div className="flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <div className="font-mono text-2xl font-bold tracking-tight">{a.account_number}</div>
                  <div className="mt-1 text-sm text-surface-600 dark:text-surface-400">
                    {a.account_name}
                  </div>
                </div>
                <button
                  onClick={() => copy(a.account_number, a.account_number)}
                  className="shrink-0 rounded-xl bg-primary-50 p-3 text-primary-700 transition hover:bg-primary-100 dark:bg-primary-900/30 dark:text-primary-400"
                  aria-label="Copy account number"
                >
                  {copied === a.account_number ? <Check className="h-5 w-5" /> : <Copy className="h-5 w-5" />}
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-5 rounded-2xl bg-primary-50 p-5 dark:bg-primary-950/30">
          <div className="mb-2 flex items-center gap-2 font-semibold text-primary-900 dark:text-primary-300">
            <ArrowUp className="h-4 w-4" />
            How to fund your wallet
          </div>
          <ol className="ml-6 list-decimal space-y-1 text-sm text-primary-900 dark:text-primary-300">
            <li>Copy your account number above</li>
            <li>Open your bank app (GTBank, Access, Kuda, Opay, etc.)</li>
            <li>Transfer any amount to the account</li>
            <li>Your wallet is credited automatically within seconds</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
