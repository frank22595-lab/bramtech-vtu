'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  ArrowRight, Phone, Wifi, Tv, Zap as ZapIcon, GraduationCap, Trophy,
  Rocket, Wallet as WalletIcon, ShoppingCart, CheckCircle, Users, TrendingUp,
  Shield, HeadphonesIcon, Clock, DollarSign, ChevronDown, Star,
} from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';

// ================= Services grid =================
export function Services() {
  const services = [
    { icon: Phone, name: 'Airtime', desc: 'All 4 networks', color: 'text-blue-600 bg-blue-50 dark:bg-blue-950' },
    { icon: Wifi, name: 'Data Bundles', desc: 'From ₦200', color: 'text-primary-700 bg-primary-50 dark:bg-primary-950' },
    { icon: Tv, name: 'DStv / GOtv', desc: 'All packages', color: 'text-purple-600 bg-purple-50 dark:bg-purple-950' },
    { icon: ZapIcon, name: 'Electricity', desc: 'All 12 DisCos', color: 'text-gold-600 bg-gold-50 dark:bg-gold-950' },
    { icon: GraduationCap, name: 'Exam Pins', desc: 'WAEC, NECO, JAMB', color: 'text-red-600 bg-red-50 dark:bg-red-950' },
    { icon: Trophy, name: 'Betting', desc: 'Bet9ja, SportyBet+', color: 'text-orange-600 bg-orange-50 dark:bg-orange-950' },
    { icon: WalletIcon, name: 'Airtime → Cash', desc: 'Convert to cash', color: 'text-teal-600 bg-teal-50 dark:bg-teal-950' },
    { icon: ShoppingCart, name: 'Bulk SMS', desc: 'For businesses', color: 'text-pink-600 bg-pink-50 dark:bg-pink-950' },
  ];

  return (
    <section className="section" id="services">
      <div className="container-x">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-display-md text-balance">Everything you need, in one place</h2>
          <p className="mt-4 text-lg text-surface-600 dark:text-surface-400">
            Stop switching between apps. Buy any digital service instantly.
          </p>
        </div>

        <div className="mt-14 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {services.map((s, i) => (
            <motion.div
              key={s.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
              viewport={{ once: true }}
              className="card-interactive text-center"
            >
              <div className={cn('mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl', s.color)}>
                <s.icon className="h-6 w-6" />
              </div>
              <h3 className="font-semibold">{s.name}</h3>
              <p className="mt-1 text-sm text-surface-600 dark:text-surface-400">{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ================= How it works =================
export function HowItWorks() {
  const steps = [
    {
      icon: Rocket,
      title: 'Create your account',
      desc: 'Sign up with your phone number in 30 seconds. No paperwork, no fees.',
    },
    {
      icon: WalletIcon,
      title: 'Fund your wallet',
      desc: 'Bank transfer to your dedicated account. Funds land instantly, no delays.',
    },
    {
      icon: ShoppingCart,
      title: 'Buy anything, anytime',
      desc: 'Airtime, data, cable, electricity — one wallet powers every purchase.',
    },
  ];

  return (
    <section className="section bg-surface-100 dark:bg-surface-900" id="how-it-works">
      <div className="container-x">
        <div className="mx-auto max-w-2xl text-center">
          <div className="mb-4 inline-block rounded-full bg-primary-100 px-3 py-1 text-xs font-semibold text-primary-800 dark:bg-primary-900/40 dark:text-primary-300">
            HOW IT WORKS
          </div>
          <h2 className="text-display-md text-balance">Get started in 3 simple steps</h2>
        </div>

        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {steps.map((s, i) => (
            <motion.div
              key={s.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="card-elevated relative h-full">
                <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-600 to-primary-800 text-white shadow-brand-glow">
                  <s.icon className="h-6 w-6" />
                </div>
                <div className="absolute right-6 top-6 text-5xl font-bold text-primary-100 dark:text-primary-900/40">
                  0{i + 1}
                </div>
                <h3 className="mb-2 text-xl font-bold">{s.title}</h3>
                <p className="text-surface-600 dark:text-surface-400">{s.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ================= Stats =================
export function Stats() {
  const stats = [
    { value: '< 2s', label: 'Average delivery time' },
    { value: '99.9%', label: 'Uptime this year' },
    { value: '4', label: 'Telco networks supported' },
    { value: '24/7', label: 'Customer support' },
  ];

  return (
    <section className="section">
      <div className="container-x">
        <div className="rounded-3xl bg-gradient-to-br from-primary-700 to-primary-900 p-8 md:p-12">
          <div className="grid gap-8 md:grid-cols-4">
            {stats.map((s) => (
              <div key={s.label} className="text-center text-white">
                <div className="text-4xl font-bold md:text-5xl">{s.value}</div>
                <div className="mt-2 text-sm text-white/80">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// ================= Feature grid (bento) =================
export function Features() {
  return (
    <section className="section">
      <div className="container-x">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-display-md text-balance">Built for Nigerians. Built to last.</h2>
          <p className="mt-4 text-lg text-surface-600 dark:text-surface-400">
            Every detail designed for how you actually use these services.
          </p>
        </div>

        <div className="mt-14 grid gap-6 md:grid-cols-6">
          <FeatureCard className="md:col-span-4" icon={Shield} title="Bank-grade security" iconColor="text-primary-700 bg-primary-100 dark:bg-primary-900/40">
            Every transaction protected by a 4-digit PIN separate from your login. Auto-lockout after 5 failed attempts. Encrypted wallet balance never exposed in transit.
          </FeatureCard>

          <FeatureCard className="md:col-span-2" icon={Clock} title="Instant refunds" iconColor="text-gold-700 bg-gold-100 dark:bg-gold-900/40">
            Failed transaction? Your wallet is refunded automatically within 30 seconds.
          </FeatureCard>

          <FeatureCard className="md:col-span-2" icon={DollarSign} title="Best prices" iconColor="text-blue-700 bg-blue-100 dark:bg-blue-900/40">
            Save on every purchase. More savings the more you buy.
          </FeatureCard>

          <FeatureCard className="md:col-span-4" icon={Users} title="Earn as a reseller" iconColor="text-purple-700 bg-purple-100 dark:bg-purple-900/40">
            Turn your phone into a business. Get exclusive reseller pricing on every service and earn margin on every sale to your customers. Bronze, Silver, Gold and Platinum tiers with progressively better rates.
          </FeatureCard>

          <FeatureCard className="md:col-span-3" icon={HeadphonesIcon} title="Real human support" iconColor="text-red-700 bg-red-100 dark:bg-red-900/40">
            WhatsApp us anytime. Real people, not chatbots. Most issues resolved within 10 minutes.
          </FeatureCard>

          <FeatureCard className="md:col-span-3" icon={TrendingUp} title="Growing every day" iconColor="text-teal-700 bg-teal-100 dark:bg-teal-900/40">
            New services added monthly. Reseller network expanding. Big things coming.
          </FeatureCard>
        </div>
      </div>
    </section>
  );
}

function FeatureCard({ icon: Icon, title, children, className, iconColor }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      viewport={{ once: true }}
      className={cn('bento', className)}
    >
      <div className={cn('mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl', iconColor)}>
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="mb-2 text-lg font-bold">{title}</h3>
      <p className="text-surface-600 dark:text-surface-400">{children}</p>
    </motion.div>
  );
}

// ================= Reseller CTA =================
export function ResellerCTA() {
  const tiers = [
    { name: 'Bronze', fee: 'Free', discount: '~15% off', color: 'from-amber-600 to-amber-800' },
    { name: 'Silver', fee: '₦2,500', discount: '~20% off', color: 'from-slate-400 to-slate-600' },
    { name: 'Gold', fee: '₦7,500', discount: '~25% off', color: 'from-gold-500 to-gold-700' },
    { name: 'Platinum', fee: '₦20,000', discount: '~30% off', color: 'from-purple-600 to-purple-900' },
  ];

  return (
    <section className="section bg-surface-100 dark:bg-surface-900" id="resellers">
      <div className="container-x">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <div className="mb-4 inline-block rounded-full bg-gold-100 px-3 py-1 text-xs font-semibold text-gold-800 dark:bg-gold-900/40 dark:text-gold-300">
              RESELLER PROGRAM
            </div>
            <h2 className="text-display-md text-balance">
              Turn your phone into <span className="text-gradient-gold">a real business</span>.
            </h2>
            <p className="mt-4 text-lg text-surface-600 dark:text-surface-400">
              Join thousands of Nigerians earning ₦25,000 to ₦230,000/month reselling airtime and data to their customers.
            </p>

            <ul className="mt-6 space-y-3">
              {[
                'Get exclusive wholesale pricing on every service',
                'Higher tier = bigger discount + higher earnings',
                'Zero monthly fees. Only pay once to upgrade',
                'API access on Gold+ for automated resellers',
                'Sub-agent management on Platinum',
              ].map((item) => (
                <li key={item} className="flex items-start gap-2">
                  <CheckCircle className="mt-0.5 h-5 w-5 shrink-0 text-primary-600" />
                  <span className="text-surface-700 dark:text-surface-300">{item}</span>
                </li>
              ))}
            </ul>

            <div className="mt-8 flex gap-3">
              <Link href="/register" className="btn-primary btn-lg">Start earning today</Link>
              <Link href="/resellers" className="btn-outline btn-lg">Learn more</Link>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {tiers.map((t, i) => (
              <motion.div
                key={t.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: i * 0.05 }}
                viewport={{ once: true }}
                className={cn('rounded-2xl bg-gradient-to-br p-5 text-white shadow-elevated', t.color)}
              >
                <div className="mb-1 text-xs uppercase tracking-wider opacity-80">{t.name}</div>
                <div className="mb-3 text-2xl font-bold">{t.fee}</div>
                <div className="text-sm opacity-90">{t.discount}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// ================= FAQ =================
export function FAQ() {
  const faqs = [
    {
      q: 'How fast is airtime and data delivery?',
      a: 'Under 2 seconds on average. Our system dispatches directly through multiple redundant aggregators, so if one is slow, your transaction routes to another automatically.',
    },
    {
      q: 'What happens if a transaction fails?',
      a: 'Your wallet is refunded automatically within 30 seconds — this is a CBN-mandated SLA and we take it seriously. You will get a notification and see the refund reflected in your balance immediately.',
    },
    {
      q: 'How do I fund my wallet?',
      a: 'Every user gets a dedicated virtual bank account (via Monnify). You transfer any amount from your bank app to that account and your wallet is credited instantly. No cards required.',
    },
    {
      q: 'Is my money safe?',
      a: 'Wallet balances are backed by a strict double-entry accounting ledger. Every naira is tracked. Every transaction has an audit trail. Your funds are held in regulated bank accounts through our licensed payment partners.',
    },
    {
      q: 'What is a "reseller tier"?',
      a: 'Reseller tiers give you progressively better prices on every service so you can resell profitably. Bronze is free, Silver is ₦2,500, Gold is ₦7,500, Platinum is ₦20,000. Higher tier = bigger discount = higher profit per sale.',
    },
    {
      q: 'Do I need a bank account?',
      a: 'You need a way to fund your wallet, which is easiest by bank transfer. Any Nigerian bank works — GTBank, Access, Zenith, Opay, Palmpay, Kuda, etc.',
    },
    {
      q: 'What if I forget my transaction PIN?',
      a: 'Contact us via WhatsApp. We will verify your identity and help you reset. After 5 wrong PIN attempts, your PIN is locked for 15 minutes for security.',
    },
    {
      q: 'Can I get a receipt for my transactions?',
      a: 'Yes. Every transaction has a permanent receipt page you can share via WhatsApp, download as PDF, or use for business expense tracking.',
    },
  ];

  const [open, setOpen] = useState<number | null>(0);

  return (
    <section className="section" id="faq">
      <div className="container-x">
        <div className="mx-auto max-w-3xl">
          <div className="text-center">
            <h2 className="text-display-md text-balance">Frequently asked questions</h2>
            <p className="mt-4 text-lg text-surface-600 dark:text-surface-400">
              Can't find what you're looking for? WhatsApp us at{' '}
              <a href="https://wa.me/2348137925907" className="link">+234 813 792 5907</a>
            </p>
          </div>

          <div className="mt-12 space-y-3">
            {faqs.map((f, i) => (
              <div key={i} className="card overflow-hidden">
                <button
                  onClick={() => setOpen(open === i ? null : i)}
                  className="flex w-full items-center justify-between text-left"
                >
                  <span className="pr-4 font-semibold">{f.q}</span>
                  <ChevronDown
                    className={cn(
                      'h-5 w-5 shrink-0 text-surface-500 transition-transform',
                      open === i && 'rotate-180'
                    )}
                  />
                </button>
                {open === i && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-3 text-surface-600 dark:text-surface-400"
                  >
                    {f.a}
                  </motion.div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// ================= Final CTA =================
export function FinalCTA() {
  return (
    <section className="section">
      <div className="container-x">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-700 via-primary-800 to-primary-950 p-8 text-center md:p-16">
          <div className="absolute inset-0 bg-grid-pattern opacity-[0.04]" />
          <div className="relative">
            <div className="mb-6 inline-flex items-center gap-1 rounded-full bg-white/15 px-3 py-1 text-xs font-semibold text-white backdrop-blur">
              <Star className="h-3 w-3 fill-current" />
              Trusted by users across Nigeria
            </div>
            <h2 className="mx-auto max-w-2xl text-display-md text-white text-balance">
              Ready to stop wasting time on slow apps?
            </h2>
            <p className="mx-auto mt-4 max-w-lg text-lg text-white/80">
              Create your free account in 30 seconds. Fund your wallet. Start buying.
            </p>
            <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
              <Link href="/register" className="btn-lg bg-white text-primary-800 hover:bg-white/90 shadow-elevated">
                Create free account
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/how-it-works" className="btn-lg border-2 border-white/30 text-white hover:bg-white/10">
                See how it works
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
