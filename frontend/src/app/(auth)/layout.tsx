import { Logo } from '../components/Logo';
import Link from 'next/link';

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative min-h-screen bg-gradient-to-br from-surface-50 via-primary-50/30 to-surface-50 dark:from-surface-950 dark:via-primary-950/20 dark:to-surface-950">
      <div className="absolute top-6 left-1/2 -translate-x-1/2 md:left-6 md:translate-x-0">
        <Logo />
      </div>
      <div className="flex min-h-screen items-center justify-center p-4 pt-24 md:pt-16">
        <div className="w-full max-w-md">{children}</div>
      </div>
      <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-20 -left-20 h-96 w-96 rounded-full bg-primary-400/10 blur-3xl" />
        <div className="absolute -bottom-20 -right-20 h-96 w-96 rounded-full bg-gold-400/10 blur-3xl" />
      </div>
    </div>
  );
}
