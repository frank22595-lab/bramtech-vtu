import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import { Providers } from '../components/Providers';
import { site } from '../lib/site';
import '@/styles/globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: {
    default: `${site.fullName} — ${site.tagline}`,
    template: `%s | ${site.name}`,
  },
  description: site.description,
  keywords: ['VTU Nigeria', 'buy airtime online', 'data bundles', 'DStv payment', 'GOtv', 'electricity bill', 'MTN airtime', 'Glo data'],
  authors: [{ name: site.company }],
  creator: site.company,
  metadataBase: new URL(site.url),
  openGraph: {
    title: site.fullName,
    description: site.description,
    url: site.url,
    siteName: site.name,
    locale: 'en_NG',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: site.fullName,
    description: site.description,
  },
  manifest: '/manifest.json',
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#087040' },
    { media: '(prefers-color-scheme: dark)', color: '#053e26' },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
