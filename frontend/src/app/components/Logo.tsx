import Link from 'next/link';
import { cn } from '../lib/utils';

interface LogoProps {
  className?: string;
  showText?: boolean;
  variant?: 'default' | 'white';
}

export function Logo({ className, showText = true, variant = 'default' }: LogoProps) {
  const textColor = variant === 'white' ? 'text-white' : 'text-surface-900 dark:text-white';

  return (
    <Link href="/" className={cn('inline-flex items-center gap-2 group', className)}>
      <div className="relative">
        <svg viewBox="0 0 40 40" className="h-9 w-9" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="40" height="40" rx="10" fill="url(#logo-grad)" />
          <path
            d="M12 12h9c3 0 5.5 2 5.5 4.8 0 1.6-.8 3-2 3.8 1.8.7 3 2.3 3 4.3 0 3-2.6 5.1-5.8 5.1H12V12z"
            fill="white"
          />
          <path d="M16 15v4h5c1.5 0 2.5-.8 2.5-2s-1-2-2.5-2h-5zm0 7v5h5.5c1.7 0 2.8-1 2.8-2.5s-1.1-2.5-2.8-2.5H16z"
            fill="url(#logo-grad)" />
          <defs>
            <linearGradient id="logo-grad" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
              <stop stopColor="#087040" />
              <stop offset="1" stopColor="#0d8f4f" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      {showText && (
        <span className={cn('text-xl font-bold tracking-tight', textColor)}>
          BRAM
          <span className="ml-0.5 text-gold-500">.</span>
        </span>
      )}
    </Link>
  );
}
