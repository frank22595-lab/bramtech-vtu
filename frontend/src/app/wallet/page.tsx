'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, formatNaira, getAccessToken } from '../api-client';

export default function WalletPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    if (!getAccessToken()) { router.push('/auth/login'); return; }
    api.get('/auth/me/').then((r) => setUser(r.data));
  }, [router]);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b p-4">
        <div className="max-w-2xl mx-auto flex justify-between items-center">
          <Link href="/dashboard" className="text-sm">← Back</Link>
          <h1 className="font-bold">Wallet</h1>
          <div className="w-12"></div>
        </div>
      </nav>
      <main className="max-w-2xl mx-auto p-4 space-y-6">
        <div className="rounded-2xl bg-gradient-to-br from-brand-700 to-brand-900 text-white p-6">
          <div className="text-xs uppercase opacity-80">Balance</div>
          <div className="text-4xl font-bold mt-2">{formatNaira(user?.wallet_balance)}</div>
        </div>

        <div className="card">
          <h2 className="font-bold text-lg mb-3">Fund your wallet</h2>
          <p className="text-gray-600 text-sm mb-4">
            Wallet funding via Monnify bank transfer is coming soon. For now, contact us on WhatsApp to fund manually.
          </p>
          <a
            href="https://wa.me/2348137925907"
            target="_blank"
            rel="noreferrer"
            className="btn btn-primary btn-lg w-full"
          >
            💬 WhatsApp Support
          </a>
        </div>
      </main>
    </div>
  );
}
