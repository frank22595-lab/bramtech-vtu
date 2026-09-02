import Link from 'next/link';
import { CheckCircle } from 'lucide-react';
import { ResellerCTA, FinalCTA } from '../../components/marketing/Sections';

export const metadata = { title: 'Pricing' };

const tiers = [
  {
    name: 'Regular',
    price: 'Free',
    desc: 'For personal use',
    features: [
      'Buy airtime, data, cable, electricity',
      'Standard retail pricing',
      'Instant delivery',
      'Auto refund on failure',
      'WhatsApp support',
    ],
    highlight: false,
  },
  {
    name: 'Bronze Reseller',
    price: 'Free',
    desc: 'Start your side hustle',
    features: [
      'Everything in Regular',
      'Approximately 15% off all services',
      'Basic transaction history',
      'Email support',
    ],
    highlight: false,
  },
  {
    name: 'Silver Reseller',
    price: '₦2,500',
    desc: 'One-time upgrade',
    features: [
      'Everything in Bronze',
      'Approximately 20% off all services',
      'Beneficiary management',
      'Priority support',
    ],
    highlight: false,
  },
  {
    name: 'Gold Reseller',
    price: '₦7,500',
    desc: 'For serious resellers',
    features: [
      'Everything in Silver',
      'Approximately 25% off all services',
      'API access for automation',
      'Bulk purchase tools',
      'Dedicated support',
    ],
    highlight: true,
  },
  {
    name: 'Platinum Reseller',
    price: '₦20,000',
    desc: 'Full VTU business',
    features: [
      'Everything in Gold',
      'Approximately 30% off all services',
      'Sub-agent management',
      'Custom branding',
      '24/7 priority support',
    ],
    highlight: false,
  },
];

export default function Page() {
  return (
    <div className="pt-24">
      <div className="container-x pt-8 text-center">
        <h1 className="text-display-lg text-balance">Simple, honest pricing</h1>
        <p className="mx-auto mt-4 max-w-xl text-lg text-surface-600 dark:text-surface-400">
          No monthly fees. No surprises. Upgrade once, save on every purchase forever.
        </p>
      </div>

      <div className="container-x mt-16">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-5">
          {tiers.map((t) => (
            <div
              key={t.name}
              className={`rounded-3xl p-6 ${
                t.highlight
                  ? 'bg-gradient-to-br from-primary-700 to-primary-900 text-white shadow-elevated ring-2 ring-gold-400'
                  : 'card'
              }`}
            >
              {t.highlight && (
                <div className="mb-3 inline-block rounded-full bg-gold-400/20 px-2 py-0.5 text-xs font-semibold text-gold-300 ring-1 ring-gold-400/40">
                  Most popular
                </div>
              )}
              <h3 className="text-lg font-bold">{t.name}</h3>
              <div className={`mt-1 text-sm ${t.highlight ? 'text-white/70' : 'text-surface-500'}`}>{t.desc}</div>
              <div className="mt-4 text-3xl font-bold">{t.price}</div>
              <ul className="mt-6 space-y-2 text-sm">
                {t.features.map((f) => (
                  <li key={f} className="flex items-start gap-2">
                    <CheckCircle className={`mt-0.5 h-4 w-4 shrink-0 ${t.highlight ? 'text-gold-400' : 'text-primary-600'}`} />
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
              <Link
                href="/register"
                className={`mt-6 block w-full rounded-xl px-4 py-2.5 text-center text-sm font-semibold transition ${
                  t.highlight
                    ? 'bg-white text-primary-800 hover:bg-white/90'
                    : 'bg-primary-700 text-white hover:bg-primary-800'
                }`}
              >
                Get started
              </Link>
            </div>
          ))}
        </div>
      </div>

      <ResellerCTA />
      <FinalCTA />
    </div>
  );
}
