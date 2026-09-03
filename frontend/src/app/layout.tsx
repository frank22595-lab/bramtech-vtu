import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'BRAM Data & Utilities',
  description: 'Airtime, Data & Bills — delivered in seconds.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
