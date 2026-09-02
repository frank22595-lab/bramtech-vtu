'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';
import { User as UserIcon, Shield, Copy, Check, Loader2, Award, CheckCircle2 } from 'lucide-react';
import { api } from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';

const TIER_LABELS: Record<string, string> = {
  regular: 'Regular User',
  bronze: 'Bronze Reseller',
  silver: 'Silver Reseller',
  gold: 'Gold Reseller',
  platinum: 'Platinum Reseller',
};

const KYC_LABELS = ['Unverified', 'Email verified', 'NIN verified', 'BVN verified'];

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const [pin, setPin] = useState('');
  const [confirmPin, setConfirmPin] = useState('');
  const [copied, setCopied] = useState(false);

  const setPinMutation = useMutation({
    mutationFn: async () => {
      if (pin !== confirmPin) throw new Error("PINs don't match");
      if (pin.length < 4) throw new Error('PIN too short');
      return (await api.post('/auth/set-pin/', { pin })).data;
    },
    onSuccess: () => {
      toast.success('PIN updated');
      setPin(''); setConfirmPin('');
    },
    onError: (e: any) => toast.error(e?.message || 'Failed to set PIN'),
  });

  if (!user) return null;

  const copyReferral = () => {
    navigator.clipboard.writeText(user.referral_code);
    setCopied(true);
    toast.success('Referral code copied');
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-display-sm">Profile</h1>

      <div className="card-elevated">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-600 to-primary-800 text-white text-2xl font-bold">
            {(user.first_name?.[0] || user.phone_number[0]).toUpperCase()}
          </div>
          <div className="flex-1">
            <div className="text-lg font-bold">{user.full_name || 'Add your name'}</div>
            <div className="text-sm text-surface-600 dark:text-surface-400">{user.phone_number}</div>
            {user.email && (
              <div className="flex items-center gap-1 text-xs text-surface-500">
                {user.email} {user.email_verified && <CheckCircle2 className="h-3 w-3 text-primary-600" />}
              </div>
            )}
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-4 border-t border-surface-100 pt-6 dark:border-surface-800">
          <div>
            <div className="flex items-center gap-1 text-xs text-surface-500">
              <Award className="h-3 w-3" /> Tier
            </div>
            <div className="mt-1 font-bold">{TIER_LABELS[user.tier]}</div>
          </div>
          <div>
            <div className="text-xs text-surface-500">KYC Level {user.kyc_tier}</div>
            <div className="mt-1 font-bold">{KYC_LABELS[user.kyc_tier]}</div>
          </div>
        </div>
      </div>

      {/* Referral */}
      <div className="rounded-3xl bg-gradient-to-br from-gold-50 to-gold-100 p-6 ring-1 ring-gold-200 dark:from-gold-950/20 dark:to-gold-900/10 dark:ring-gold-900/40">
        <h3 className="font-bold">Your referral code</h3>
        <p className="mt-1 text-sm text-surface-700 dark:text-surface-300">Share with friends. Earn on every signup.</p>
        <div className="mt-4 flex items-center gap-2">
          <div className="flex-1 rounded-xl bg-white px-4 py-3 font-mono text-lg font-bold dark:bg-surface-900">
            {user.referral_code}
          </div>
          <button onClick={copyReferral} className="btn-gold">
            {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Transaction PIN */}
      <div className="card-elevated">
        <div className="mb-4 flex items-center gap-2">
          <Shield className="h-5 w-5 text-primary-700" />
          <h2 className="text-lg font-bold">Transaction PIN</h2>
        </div>
        <p className="mb-4 text-sm text-surface-600 dark:text-surface-400">
          4–6 digit PIN required for every purchase. Keep it private.
        </p>

        <div className="space-y-3">
          <div>
            <label className="label">New PIN</label>
            <input
              type="password"
              inputMode="numeric"
              placeholder="4–6 digits"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))}
              className="input text-center tracking-[0.5em] text-lg"
              maxLength={6}
            />
          </div>
          <div>
            <label className="label">Confirm PIN</label>
            <input
              type="password"
              inputMode="numeric"
              placeholder="Repeat"
              value={confirmPin}
              onChange={(e) => setConfirmPin(e.target.value.replace(/\D/g, ''))}
              className="input text-center tracking-[0.5em] text-lg"
              maxLength={6}
            />
          </div>
          <button
            onClick={() => setPinMutation.mutate()}
            disabled={setPinMutation.isPending || pin.length < 4 || pin !== confirmPin}
            className="btn-primary w-full"
          >
            {setPinMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Update PIN'}
          </button>
        </div>
      </div>

      <button onClick={logout} className="btn-outline w-full text-danger border-red-200 hover:bg-red-50 hover:border-red-300">
        Sign out
      </button>
    </div>
  );
}
