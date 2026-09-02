'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { toast } from 'sonner';
import { Loader2, Eye, EyeOff, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const schema = z.object({
  phone_number: z.string().min(10, 'Enter a valid Nigerian phone number'),
  password: z.string().min(8, 'Minimum 8 characters'),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  referral_code: z.string().optional(),
});
type FormData = z.infer<typeof schema>;

export default function RegisterPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { register: registerUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      referral_code: searchParams.get('ref') || '',
    },
  });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    try {
      await registerUser({
        ...data,
        email: data.email || undefined,
        referral_code: data.referral_code || undefined,
      });
      toast.success('Account created — welcome!');
      router.push('/dashboard');
    } catch (e: any) {
      const errs = e?.response?.data;
      if (errs && typeof errs === 'object') {
        const first = Object.values(errs)[0];
        toast.error(Array.isArray(first) ? first[0] : String(first));
      } else {
        toast.error('Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card-elevated animate-scale-in">
      <div className="mb-8">
        <h1 className="text-display-sm">Create your account</h1>
        <p className="mt-2 text-surface-600 dark:text-surface-400">
          Get started in 30 seconds
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="label">
            Phone number <span className="text-danger">*</span>
          </label>
          <input
            {...register('phone_number')}
            type="tel"
            placeholder="08012345678"
            className="input"
            autoComplete="tel"
            autoFocus
          />
          {errors.phone_number && <p className="mt-1.5 text-xs text-danger">{errors.phone_number.message}</p>}
        </div>

        <div>
          <label className="label">
            Password <span className="text-danger">*</span>
          </label>
          <div className="relative">
            <input
              {...register('password')}
              type={showPassword ? 'text' : 'password'}
              placeholder="Minimum 8 characters"
              className="input pr-10"
              autoComplete="new-password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 flex items-center px-3 text-surface-500 hover:text-surface-700"
              aria-label="Toggle password visibility"
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {errors.password && <p className="mt-1.5 text-xs text-danger">{errors.password.message}</p>}
        </div>

        <div>
          <div className="flex items-center justify-between">
            <label className="label mb-0">Email</label>
            <span className="text-xs text-primary-700 dark:text-primary-400">Recommended</span>
          </div>
          <input {...register('email')} type="email" placeholder="you@example.com" className="input mt-1.5" />
          <p className="mt-1.5 flex items-center gap-1 text-xs text-surface-500">
            <CheckCircle2 className="h-3 w-3 text-primary-600" />
            Unlocks free OTPs and account recovery
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">First name</label>
            <input {...register('first_name')} type="text" placeholder="Bright" className="input" />
          </div>
          <div>
            <label className="label">Last name</label>
            <input {...register('last_name')} type="text" placeholder="Amasunya" className="input" />
          </div>
        </div>

        <div>
          <label className="label">Referral code <span className="text-surface-400">(optional)</span></label>
          <input {...register('referral_code')} type="text" placeholder="Friend's code" className="input uppercase" />
        </div>

        <button type="submit" disabled={loading} className="btn-primary btn-lg w-full">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : (
            <>
              Create account <ArrowRight className="h-4 w-4" />
            </>
          )}
        </button>

        <p className="text-center text-xs text-surface-500">
          By signing up, you agree to our{' '}
          <Link href="/terms" className="link">Terms</Link>{' '}
          and{' '}
          <Link href="/privacy" className="link">Privacy Policy</Link>.
        </p>
      </form>

      <p className="mt-6 text-center text-sm text-surface-600 dark:text-surface-400">
        Already have an account?{' '}
        <Link href="/login" className="link">Sign in</Link>
      </p>
    </div>
  );
}
