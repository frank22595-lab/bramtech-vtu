'use client';

import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Phone, Wifi, Tv, Zap, GraduationCap, Trophy, ArrowRight, ArrowUp,
  Wallet as WalletIcon, ShoppingBag, Copy, Sparkles, Eye, EyeOff, MessageCircle,
} from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';
import { api } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { formatNaira, formatDate, statusBadgeClass, timeAgo, networkLogo, cn } from '../lib/utils';
import { Transaction } from '../types';

const QUICK = [
  { href: '/buy/airtime', icon: Phone, label: 'Airtime', color: 'from-blue-500 to-blue-700' },
  { href: '/buy/data', icon: Wifi, label: 'Data', color: 'from-primary-500 to-primary-700' },
  { href: '/buy/cable', icon: Tv, label: 'Cable', color: 'from-purple-500 to-purple-700' },
  { href: '/buy/electricity', icon: Zap, label: 'Electricity', color: 'from-gold-500 to-gold-700' },
];

const COMING_SOON = [
  { icon: GraduationCap, label: 'Exam Pins' },
  { icon: Trophy, label: 'Betting' },
  { icon: ArrowUp, label: 'Airtime → Cash' },
  { icon: MessageCircle, label: 'Bulk SMS' },
];

const TIER_LABELS: Record<string, string> = {
  regular: 'Regular',
  bronze: 'Bronze Reseller',
  silver: 'Silver Reseller',
  gold: 'Gold Reseller',
  platinum: 'Platinum Reseller',
};

export default function DashboardPage() {
  const { user } = useAuth();
  const [hideBalance, setHideBalance] = useState(false);

  const { data: txns } = useQuery<{ results: Transaction[] }>({
    queryKey: ['recent-transactions'],
    queryFn: async () => (await api.get('/transactions/?limit=5')).data,
  });

  const copyReferral = () => {
    if (!user) return;
    navigator.clipboard.writeText(user.referral_code);
    toast.success('Referral code copied');
  };

  const firstName = user?.first_name || 'there';

  return (
    <div className="space-y-8">
      {/* Greeting */}
      <div>
        <h1 className="text-display-sm">Hello, {firstName} 👋</h1>
        <p className="mt-1 text-surface-600 dark:text-surface-400">
          What would you like to buy today?
        </p>
      </div>

      {/* Wallet card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-700 via-primary-800 to-primary-950 p-6 text-white shadow-elevated md:p-8"
      >
        <div className="absolute -right-8 -top-8 h-40 w-40 rounded-full bg-white/5 blur-2xl" />
        <div className="absolute -bottom-16 -left-16 h-56 w-56 rounded-full bg-gold-500/10 blur-3xl" />
        <div className="absolute inset-0 bg-grid-pattern opacity-[0.03]" />

        <div className="relative">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase tracking-wider text-white/70">Wallet Balance</span>
                <button
                  onClick={() => setHideBalance(!hideBalance)}
                  className="text-white/70 hover:text-white"
                  aria-label={hideBalance ? 'Show balance' : 'Hide balance'}
                >
                  {hideBalance ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                </button>
              </div>
              <div className="mt-1 text-4xl font-bold tracking-tight md:text-5xl">
                {hideBalance ? '••••••' : formatNaira(user?.wallet_balance ?? '0')}
              </div>
            </div>
            {user?.tier && user.tier !== 'regular' && (
              <div className="rounded-full bg-gold-500/20 px-3 py-1 text-xs font-semibold text-gold-300 ring-1 ring-gold-500/30">
                {TIER_LABELS[user.tier]}
              </div>
            )}
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href="/wallet"
              className="inline-flex items-center gap-2 rounded-xl bg-white/15 px-5 py-2.5 text-sm font-semibold backdrop-blur transition hover:bg-white/25"
            >
              <ArrowUp className="h-4 w-4" /> Fund wallet
            </Link>
            <Link
              href="/transactions"
              className="inline-flex items-center gap-2 rounded-xl bg-white/15 px-5 py-2.5 text-sm font-semibold backdrop-blur transition hover:bg-white/25"
            >
              History <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </motion.div>

      {/* Quick buy */}
      <div>
        <h2 className="mb-4 text-lg font-bold">Quick Buy</h2>
        <div className="grid grid-cols-4 gap-3">
          {QUICK.map((q, i) => (
            <motion.div
              key={q.href}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
            >
              <Link
                href={q.href}
                className="group flex flex-col items-center gap-3 rounded-2xl bg-white p-4 shadow-soft ring-1 ring-black/5 transition-all hover:-translate-y-0.5 hover:shadow-card dark:bg-surface-900 dark:ring-white/5"
              >
                <div className={cn('flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br text-white shadow-lg transition-transform group-hover:scale-110', q.color)}>
                  <q.icon className="h-5 w-5" />
                </div>
                <span className="text-xs font-semibold">{q.label}</span>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Referral card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
        className="rounded-3xl bg-gradient-to-br from-gold-50 to-gold-100 p-6 ring-1 ring-gold-200 dark:from-gold-950/20 dark:to-gold-900/10 dark:ring-gold-900/40"
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-gold-600" />
              <h3 className="font-bold">Earn ₦100 per friend</h3>
            </div>
            <p className="mt-1 text-sm text-surface-700 dark:text-surface-300">
              Share your code. When a friend signs up and does their first ₦500+ transaction, you both earn.
            </p>
          </div>
        </div>
        <div className="mt-4 flex items-center gap-2">
          <div className="flex-1 rounded-xl bg-white px-4 py-3 font-mono text-lg font-bold dark:bg-surface-900">
            {user?.referral_code}
          </div>
          <button onClick={copyReferral} className="btn-gold">
            <Copy className="h-4 w-4" />
          </button>
        </div>
      </motion.div>

      {/* Coming soon */}
      <div>
        <h2 className="mb-4 text-lg font-bold">More Services</h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {COMING_SOON.map((s) => (
            <div key={s.label} className="flex items-center gap-3 rounded-2xl bg-white p-4 shadow-soft ring-1 ring-black/5 opacity-60 dark:bg-surface-900 dark:ring-white/5">
              <s.icon className="h-5 w-5 text-surface-500" />
              <div>
                <div className="text-sm font-semibold">{s.label}</div>
                <div className="text-xs text-surface-500">Coming soon</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent transactions */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold">Recent Activity</h2>
          <Link href="/transactions" className="text-sm text-primary-700 hover:underline dark:text-primary-400">
            See all
          </Link>
        </div>

        {!txns?.results?.length ? (
          <div className="card text-center py-12">
            <ShoppingBag className="mx-auto mb-3 h-10 w-10 text-surface-300" />
            <div className="font-semibold">No transactions yet</div>
            <div className="mt-1 text-sm text-surface-500">
              Buy something to see it here
            </div>
          </div>
        ) : (
          <div className="card divide-y divide-surface-100 dark:divide-surface-800">
            {txns.results.map((t) => {
              const logo = networkLogo(t.network);
              return (
                <Link
                  key={t.public_id}
                  href={`/transactions/${t.reference}`}
                  className="flex items-center gap-3 py-3 first:pt-0 last:pb-0 hover:bg-surface-50 dark:hover:bg-surface-900/50 -mx-6 px-6 first:rounded-t-2xl last:rounded-b-2xl"
                >
                  <div className={cn('flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-xs font-bold', logo.bg, logo.text)}>
                    {logo.short}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="truncate font-semibold text-sm">{t.variation_name}</div>
                    <div className="text-xs text-surface-500">
                      {t.recipient} · {timeAgo(t.created_at)}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-sm">{formatNaira(t.sale_price)}</div>
                    <span className={statusBadgeClass(t.status)}>{t.status}</span>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
