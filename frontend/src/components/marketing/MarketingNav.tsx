'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Logo } from '@/components/Logo';
import { site } from '@/lib/site';
import { cn } from '@/lib/utils';

export function MarketingNav() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 10);
    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
      <header
        className={cn(
          'fixed inset-x-0 top-0 z-50 transition-all duration-300',
          scrolled
            ? 'glass border-b border-surface-200/60 dark:border-surface-800/60'
            : 'bg-transparent'
        )}
      >
        <div className="container-x">
          <div className="flex h-16 items-center justify-between">
            <Logo />

            {/* Desktop nav */}
            <nav className="hidden items-center gap-1 md:flex">
              {site.nav.marketing.map((n) => (
                <Link key={n.href} href={n.href} className="nav-item">
                  {n.label}
                </Link>
              ))}
            </nav>

            <div className="hidden items-center gap-3 md:flex">
              <Link href="/login" className="btn-ghost btn-sm">Log in</Link>
              <Link href="/register" className="btn-primary btn-sm">Get Started</Link>
            </div>

            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="p-2 md:hidden"
              aria-label="Menu"
            >
              {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed inset-x-0 top-16 z-40 glass border-b border-surface-200 dark:border-surface-800 md:hidden"
          >
            <div className="container-x space-y-1 py-4">
              {site.nav.marketing.map((n) => (
                <Link
                  key={n.href}
                  href={n.href}
                  onClick={() => setMobileOpen(false)}
                  className="nav-item block"
                >
                  {n.label}
                </Link>
              ))}
              <div className="divider" />
              <div className="grid grid-cols-2 gap-2">
                <Link href="/login" className="btn-outline">Log in</Link>
                <Link href="/register" className="btn-primary">Get Started</Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
