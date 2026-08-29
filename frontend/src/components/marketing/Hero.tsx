'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Zap, Shield, CheckCircle2, Wifi, Phone, Tv, Zap as ZapIcon } from 'lucide-react';
import { formatNaira } from '@/lib/utils';

export function Hero() {
  return (
    <section className="relative overflow-hidden pt-32 pb-20 md:pt-40 md:pb-32">
      {/* Background gradients */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-primary-50/50 via-transparent to-transparent dark:from-primary-950/30" />
        <div className="absolute -top-40 left-1/2 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-primary-500/10 blur-3xl" />
        <div className="absolute top-40 right-0 h-[400px] w-[400px] rounded-full bg-gold-500/10 blur-3xl" />
      </div>

      <div className="container-x">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          {/* Left: Text */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary-100 px-4 py-1.5 text-xs font-semibold text-primary-800 ring-1 ring-primary-200 dark:bg-primary-900/40 dark:text-primary-300 dark:ring-primary-800"
            >
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary-400 opacity-75"></span>
                <span className="relative inline-flex h-2 w-2 rounded-full bg-primary-500"></span>
              </span>
              Live — 24/7 service delivery
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-display-lg md:text-display-xl text-balance"
            >
              Airtime, data & bills.{' '}
              <span className="text-gradient-brand">Delivered in seconds.</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="mt-6 max-w-lg text-lg text-surface-600 dark:text-surface-400 text-pretty"
            >
              Buy airtime, data, DStv, GOtv and pay electricity bills for any Nigerian network.
              One wallet. Instant delivery. Best prices.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="mt-8 flex flex-col gap-3 sm:flex-row"
            >
              <Link href="/register" className="btn-primary btn-lg group">
                Get Started Free
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link href="/how-it-works" className="btn-outline btn-lg">
                See how it works
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="mt-8 flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-surface-600 dark:text-surface-400"
            >
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-primary-600" />
                No signup fee
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-primary-600" />
                Instant delivery
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-primary-600" />
                Auto refund on failure
              </div>
            </motion.div>
          </div>

          {/* Right: Phone mockup */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative mx-auto max-w-md"
          >
            <PhoneMockup />
          </motion.div>
        </div>
      </div>
    </section>
  );
}

function PhoneMockup() {
  return (
    <div className="relative">
      {/* Floating badges */}
      <motion.div
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        className="absolute -left-4 top-16 z-20 rounded-2xl bg-white p-3 shadow-elevated ring-1 ring-black/5 dark:bg-surface-900 dark:ring-white/10"
      >
        <div className="flex items-center gap-2">
          <div className="rounded-full bg-primary-100 p-2 dark:bg-primary-900/40">
            <Zap className="h-4 w-4 text-primary-700 dark:text-primary-400" />
          </div>
          <div>
            <div className="text-xs font-semibold">Airtime sent</div>
            <div className="text-xs text-surface-500">1.2s ago</div>
          </div>
        </div>
      </motion.div>

      <motion.div
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
        className="absolute -right-4 top-48 z-20 rounded-2xl bg-white p-3 shadow-elevated ring-1 ring-black/5 dark:bg-surface-900 dark:ring-white/10"
      >
        <div className="flex items-center gap-2">
          <div className="rounded-full bg-gold-100 p-2 dark:bg-gold-900/40">
            <Shield className="h-4 w-4 text-gold-700 dark:text-gold-400" />
          </div>
          <div>
            <div className="text-xs font-semibold">Wallet secured</div>
            <div className="text-xs text-surface-500">PIN protected</div>
          </div>
        </div>
      </motion.div>

      {/* Phone frame */}
      <div className="relative mx-auto w-full max-w-sm rounded-[3rem] border-[10px] border-surface-900 bg-surface-900 shadow-elevated dark:border-surface-800">
        <div className="relative overflow-hidden rounded-[2.25rem] bg-gradient-to-b from-primary-50 to-white dark:from-surface-900 dark:to-surface-950">
          {/* Notch */}
          <div className="absolute left-1/2 top-2 z-10 h-6 w-24 -translate-x-1/2 rounded-full bg-surface-900"></div>

          {/* App content */}
          <div className="p-5 pt-10">
            {/* Wallet card */}
            <div className="rounded-2xl bg-gradient-to-br from-primary-700 to-primary-900 p-5 text-white shadow-lg">
              <div className="mb-1 text-xs opacity-80">Wallet Balance</div>
              <div className="text-3xl font-bold">{formatNaira(25400)}</div>
              <div className="mt-3 flex gap-2">
                <div className="flex-1 rounded-lg bg-white/15 py-1.5 text-center text-xs font-semibold backdrop-blur">
                  Fund
                </div>
                <div className="flex-1 rounded-lg bg-white/15 py-1.5 text-center text-xs font-semibold backdrop-blur">
                  History
                </div>
              </div>
            </div>

            {/* Quick tiles */}
            <div className="mt-5 grid grid-cols-4 gap-3">
              {[
                { icon: Phone, label: 'Airtime', color: 'bg-blue-100 text-blue-700' },
                { icon: Wifi, label: 'Data', color: 'bg-primary-100 text-primary-700' },
                { icon: Tv, label: 'Cable', color: 'bg-purple-100 text-purple-700' },
                { icon: ZapIcon, label: 'Power', color: 'bg-gold-100 text-gold-700' },
              ].map((q) => (
                <div key={q.label} className="flex flex-col items-center gap-1">
                  <div className={`rounded-xl p-3 ${q.color}`}>
                    <q.icon className="h-4 w-4" />
                  </div>
                  <span className="text-[10px] font-medium text-surface-700 dark:text-surface-300">{q.label}</span>
                </div>
              ))}
            </div>

            {/* Recent transactions */}
            <div className="mt-5">
              <div className="mb-2 text-xs font-semibold text-surface-700 dark:text-surface-300">Recent</div>
              <div className="space-y-2">
                {[
                  { name: 'MTN 1GB', to: '0803****', amount: '500', ok: true },
                  { name: 'DStv Compact', to: '1234567890', amount: '15,700', ok: true },
                  { name: 'IKEDC', to: '4567 8912 34', amount: '3,000', ok: true },
                ].map((t, i) => (
                  <div key={i} className="flex items-center justify-between rounded-lg bg-white p-2 shadow-soft dark:bg-surface-800">
                    <div>
                      <div className="text-xs font-semibold">{t.name}</div>
                      <div className="text-[10px] text-surface-500">{t.to}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs font-bold">₦{t.amount}</div>
                      <div className="text-[10px] text-primary-600">✓ Success</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
