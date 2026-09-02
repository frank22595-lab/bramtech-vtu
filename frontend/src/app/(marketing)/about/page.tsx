import { site } from '../lib/site';

export const metadata = { title: 'About us' };

export default function Page() {
  return (
    <div className="pt-24 pb-24">
      <div className="container-x max-w-3xl">
        <h1 className="text-display-lg text-balance">About BRAM</h1>
        <p className="mt-6 text-lg text-surface-600 dark:text-surface-400">
          BRAM Data & Utilities is built by <strong>{site.company}</strong>, based in {site.address}. We started BRAM because paying for airtime, data and bills in Nigeria still felt slower and less reliable than it should be in 2026.
        </p>

        <div className="prose prose-lg dark:prose-invert mt-10 max-w-none">
          <h2>Our mission</h2>
          <p>
            Make digital purchases as instant, cheap and reliable as sending a text message.
            Whether you're topping up your phone at 2am, funding a business, or building a
            reselling side-hustle — BRAM should be the fastest, most trusted way to do it.
          </p>

          <h2>Why we're different</h2>
          <ul>
            <li><strong>Speed:</strong> Sub-2-second delivery through redundant aggregator routing.</li>
            <li><strong>Trust:</strong> Every naira tracked in a strict double-entry ledger. Automatic 30-second refunds on any failure.</li>
            <li><strong>Fairness:</strong> Reseller pricing that grows with you. No hidden fees.</li>
            <li><strong>Support:</strong> Real humans on WhatsApp, not chatbots that go in circles.</li>
          </ul>

          <h2>Get in touch</h2>
          <p>
            We'd love to hear from you. Reach us on WhatsApp at{' '}
            <a href={`https://wa.me/${site.whatsapp.replace(/\D/g, '')}`} className="link">{site.phone}</a>{' '}
            or email <a href={`mailto:${site.email}`} className="link">{site.email}</a>.
          </p>
        </div>
      </div>
    </div>
  );
}
