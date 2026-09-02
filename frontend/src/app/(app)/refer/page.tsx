'use client';

import { useState } from 'react';
import { Copy, Check, Sparkles, Share2, MessageCircle } from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '../contexts/AuthContext';
import { site } from '../lib/site';

export default function ReferPage() {
  const { user } = useAuth();
  const [copied, setCopied] = useState(false);

  if (!user) return null;

  const referralLink = `${site.url}/register?ref=${user.referral_code}`;

  const copy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success('Copied');
    setTimeout(() => setCopied(false), 1500);
  };

  const shareText = `Hey! I use BRAM for airtime, data, cable and bills — it's fast and cheap. Sign up with my code and we both earn: ${referralLink}`;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-display-sm">Refer & Earn</h1>
        <p className="mt-1 text-surface-600 dark:text-surface-400">
          Earn ₦100 for every friend who signs up and transacts.
        </p>
      </div>

      <div className="rounded-3xl bg-gradient-to-br from-gold-500 to-gold-700 p-8 text-white shadow-elevated">
        <Sparkles className="mb-3 h-8 w-8" />
        <div className="text-xs uppercase tracking-wider opacity-80">Your referral code</div>
        <div className="mt-2 text-5xl font-bold tracking-tight">{user.referral_code}</div>
        <button
          onClick={() => copy(user.referral_code)}
          className="mt-6 inline-flex items-center gap-2 rounded-xl bg-white/15 px-4 py-2 text-sm font-semibold backdrop-blur hover:bg-white/25"
        >
          {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
          Copy code
        </button>
      </div>

      <div className="card">
        <h2 className="mb-4 text-lg font-bold">Share your link</h2>
        <div className="rounded-xl bg-surface-100 p-3 text-sm font-mono break-all dark:bg-surface-800">
          {referralLink}
        </div>
        <div className="mt-4 grid grid-cols-2 gap-3">
          <a
            href={`https://wa.me/?text=${encodeURIComponent(shareText)}`}
            target="_blank"
            rel="noreferrer"
            className="btn-primary"
          >
            <MessageCircle className="h-4 w-4" /> WhatsApp
          </a>
          <button onClick={() => copy(referralLink)} className="btn-secondary">
            <Share2 className="h-4 w-4" /> Copy link
          </button>
        </div>
      </div>

      <div className="card">
        <h2 className="mb-4 text-lg font-bold">How it works</h2>
        <ol className="ml-5 list-decimal space-y-2 text-sm text-surface-700 dark:text-surface-300">
          <li>Share your code with friends</li>
          <li>They sign up and enter your code</li>
          <li>When they complete their first ₦500+ transaction, you earn ₦100</li>
          <li>Rewards credit automatically to your wallet</li>
        </ol>
      </div>
    </div>
  );
}
