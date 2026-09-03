'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { api, formatNaira, getAccessToken } from '../api-client';

function TransactionsInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const ref = searchParams.get('ref');

  const [items, setItems] = useState<any[]>([]);
  const [detail, setDetail] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!getAccessToken()) { router.push('/auth/login'); return; }

    if (ref) {
      const fetchDetail = () => {
        api.get(`/transactions/${ref}/`).then((r) => {
          setDetail(r.data);
          setLoading(false);
          if (r.data.status === 'processing' || r.data.status === 'pending') {
            setTimeout(fetchDetail, 2000);
          }
        }).catch(() => setLoading(false));
      };
      fetchDetail();
    } else {
      api.get('/transactions/').then((r) => {
        setItems(r.data.results || []);
        setLoading(false);
      }).catch(() => setLoading(false));
    }
  }, [ref, router]);

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  if (ref && detail) {
    const isSuccess = detail.status === 'success';
    const isFailed = detail.status === 'failed';
    const isPending = detail.status === 'processing' || detail.status === 'pending';

    return (
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white border-b p-4">
          <div className="max-w-lg mx-auto flex justify-between">
            <Link href="/transactions" className="text-sm">← Back</Link>
            <h1 className="font-bold">Receipt</h1>
            <div className="w-12"></div>
          </div>
        </nav>
        <main className="max-w-lg mx-auto p-4">
          <div className="card">
            <div className="text-center py-6">
              <div className="text-5xl mb-3">
                {isSuccess ? '✅' : isFailed ? '❌' : '⏳'}
              </div>
              <div className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase ${
                isSuccess ? 'bg-green-100 text-green-800' :
                isFailed ? 'bg-red-100 text-red-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {detail.status}
              </div>
              <div className="text-4xl font-bold mt-4">{formatNaira(detail.sale_price)}</div>
              <div className="mt-1 text-gray-600">{detail.variation_name}</div>
            </div>
            <hr className="my-4" />
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-500">Reference</span><span className="font-mono text-xs">{detail.reference}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Recipient</span><span className="font-mono">{detail.recipient}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Network</span><span className="uppercase">{detail.network}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Date</span><span>{new Date(detail.created_at).toLocaleString()}</span></div>
              {detail.status_message && (
                <div className="flex justify-between"><span className="text-gray-500">Note</span><span className="text-right max-w-[60%]">{detail.status_message}</span></div>
              )}
            </div>
            {isPending && (
              <div className="mt-4 p-3 bg-yellow-50 rounded-lg text-center text-xs text-yellow-800">
                ⏳ Processing — page will auto-update
              </div>
            )}
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2">
            <Link href="/dashboard" className="btn btn-outline">Dashboard</Link>
            <Link href={`/buy/${detail.transaction_type}`} className="btn btn-primary">Buy Again</Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b p-4">
        <div className="max-w-2xl mx-auto flex justify-between">
          <Link href="/dashboard" className="text-sm">← Back</Link>
          <h1 className="font-bold">Transactions</h1>
          <div className="w-12"></div>
        </div>
      </nav>
      <main className="max-w-2xl mx-auto p-4">
        {items.length === 0 ? (
          <div className="card text-center py-12">
            <div className="text-4xl mb-2">📭</div>
            <div className="font-semibold">No transactions yet</div>
            <div className="text-sm text-gray-500 mt-1">Purchases will appear here</div>
          </div>
        ) : (
          <div className="card divide-y">
            {items.map((t) => (
              <Link key={t.public_id} href={`/transactions?ref=${t.reference}`}
                className="flex justify-between py-3 first:pt-0 last:pb-0 hover:bg-gray-50 -mx-6 px-6">
                <div>
                  <div className="font-semibold text-sm">{t.variation_name}</div>
                  <div className="text-xs text-gray-500">{t.recipient}</div>
                </div>
                <div className="text-right">
                  <div className="font-bold">{formatNaira(t.sale_price)}</div>
                  <div className={`text-xs ${
                    t.status === 'success' ? 'text-green-700' :
                    t.status === 'failed' ? 'text-red-700' :
                    'text-yellow-700'
                  }`}>{t.status}</div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default function TransactionsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <TransactionsInner />
    </Suspense>
  );
}
