'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, setTokens } from '../../api-client';

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ phone_number: '', password: '', email: '', first_name: '', last_name: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload: any = { phone_number: form.phone_number, password: form.password };
      if (form.email) payload.email = form.email;
      if (form.first_name) payload.first_name = form.first_name;
      if (form.last_name) payload.last_name = form.last_name;
      const { data } = await api.post('/auth/register/', payload);
      setTokens(data.access, data.refresh);
      router.push('/dashboard');
    } catch (err: any) {
      const errs = err?.response?.data;
      if (errs && typeof errs === 'object') {
        const first = Object.values(errs)[0];
        setError(Array.isArray(first) ? String(first[0]) : String(first));
      } else {
        setError('Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };

  const upd = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) => setForm({ ...form, [k]: e.target.value });

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-brand-50 to-white">
      <div className="w-full max-w-md">
        <Link href="/" className="flex items-center gap-2 mb-8 justify-center">
          <div className="w-9 h-9 rounded-lg bg-brand-700 flex items-center justify-center text-white font-bold">B</div>
          <span className="font-bold text-xl">BRAM<span className="text-gold-500">.</span></span>
        </Link>
        <div className="card">
          <h1 className="text-2xl font-bold mb-2">Create your account</h1>
          <p className="text-gray-600 mb-6">Get started in 30 seconds</p>

          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="label">Phone number *</label>
              <input type="tel" value={form.phone_number} onChange={upd('phone_number')} className="input" placeholder="08012345678" required />
            </div>
            <div>
              <label className="label">Password *</label>
              <input type="password" value={form.password} onChange={upd('password')} className="input" placeholder="Min 8 characters" required minLength={8} />
            </div>
            <div>
              <label className="label">Email (recommended)</label>
              <input type="email" value={form.email} onChange={upd('email')} className="input" placeholder="you@example.com" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">First name</label>
                <input type="text" value={form.first_name} onChange={upd('first_name')} className="input" />
              </div>
              <div>
                <label className="label">Last name</label>
                <input type="text" value={form.last_name} onChange={upd('last_name')} className="input" />
              </div>
            </div>
            {error && <p className="text-red-600 text-sm">{error}</p>}
            <button type="submit" disabled={loading} className="btn btn-primary btn-lg w-full">
              {loading ? 'Creating...' : 'Create account →'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-600 mt-6">
            Already have an account?{' '}
            <Link href="/auth/login" className="text-brand-700 font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
