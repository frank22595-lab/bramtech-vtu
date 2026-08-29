'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  Home, Wallet as WalletIcon, ShoppingBag, User, LogOut, Loader2,
  Bell, ChevronDown,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Logo } from '@/components/Logo';
import { formatNaira } from '@/lib/utils';
import { site } from '@/lib/site';
import { cn } from '@/lib/utils';

const NAV = [
  { href: '/dashboard', label: 'Home', icon: Home },
  { href: '/wallet', label: 'Wallet', icon: WalletIcon },
  { href: '/transactions', label: 'History', icon: ShoppingBag },
  { href: '/profile', label: 'Profile', icon: User },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) router.push('/login');
  }, [loading, user, router]);

  if (loading) return (
    <div className="flex min-h-screen items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
    </div>
  );
  if (!user) return null;

  const isActive = (href: string) => pathname === href || (href !== '/dashboard' && pathname?.startsWith(href));

  return (
    <div className="min-h-screen bg-surface-50 pb-24 md:pb-0 dark:bg-surface-950">
      {/* Top bar */}
      <header className="sticky top-0 z-30 glass border-b border-surface-200/60 dark:border-surface-800/60">
        <div className="container-x">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-8">
              <Logo />
              <nav className="hidden gap-1 md:flex">
                {NAV.map((n) => (
                  <Link
                    key={n.href}
                    href={n.href}
                    className={isActive(n.href) ? 'nav-item-active' : 'nav-item'}
                  >
                    <n.icon className="h-4 w-4" /> {n.label}
                  </Link>
                ))}
              </nav>
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden md:block text-right">
                <div className="text-xs text-surface-500">Wallet balance</div>
                <div className="font-bold text-primary-700 dark:text-primary-400">
                  {formatNaira(user.wallet_balance)}
                </div>
              </div>
              <button className="rounded-full p-2 hover:bg-surface-100 dark:hover:bg-surface-800" aria-label="Notifications">
                <Bell className="h-5 w-5" />
              </button>
              <button
                onClick={logout}
                className="rounded-full p-2 text-danger hover:bg-red-50 dark:hover:bg-red-950"
                aria-label="Sign out"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container-x py-6 md:py-10">
        <motion.div
          key={pathname}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {children}
        </motion.div>
      </main>

      {/* Mobile bottom nav */}
      <nav className="fixed bottom-0 left-0 right-0 z-30 glass border-t border-surface-200 dark:border-surface-800 md:hidden">
        <div className="grid grid-cols-4 py-2">
          {NAV.map((n) => (
            <Link
              key={n.href}
              href={n.href}
              className={cn(
                'flex flex-col items-center gap-1 py-2 text-xs',
                isActive(n.href)
                  ? 'text-primary-700 dark:text-primary-400'
                  : 'text-surface-500 dark:text-surface-500'
              )}
            >
              <n.icon className={cn('h-5 w-5', isActive(n.href) && 'stroke-[2.5]')} />
              {n.label}
            </Link>
          ))}
        </div>
      </nav>
    </div>
  );
}
