import { site } from '../lib/site';

export const metadata = { title: 'Privacy Policy' };

export default function Page() {
  return (
    <>
      <h1>Privacy Policy</h1>
      <p><em>Last updated: August 2026</em></p>

      <p>{site.company} respects your privacy. This policy explains what we collect, why, and what you can do about it.</p>

      <h2>What we collect</h2>
      <ul>
        <li><strong>Account info:</strong> phone number, email (if provided), name.</li>
        <li><strong>Transaction data:</strong> what you buy, when, and for whom (recipient phone/meter/smartcard).</li>
        <li><strong>Wallet data:</strong> balance, funding history.</li>
        <li><strong>Device data:</strong> IP address, browser, device type — for security only.</li>
      </ul>

      <h2>Why we collect it</h2>
      <ul>
        <li>To deliver the services you request</li>
        <li>To prevent fraud and secure your account</li>
        <li>To comply with legal requirements</li>
        <li>To improve BRAM based on aggregated usage</li>
      </ul>

      <h2>Who we share it with</h2>
      <p>We share only what is necessary with:</p>
      <ul>
        <li><strong>Payment providers</strong> (e.g. Monnify) — to process wallet funding</li>
        <li><strong>Service aggregators</strong> — the recipient phone/meter to fulfill your purchase</li>
        <li><strong>Nigerian authorities</strong> — only when legally compelled</li>
      </ul>
      <p>We do NOT sell your data to advertisers or third parties.</p>

      <h2>Data retention</h2>
      <p>
        Transaction records are kept indefinitely for legal, accounting and dispute-resolution purposes. Personal profile data is kept as long as your account is active. You can request deletion by contacting us.
      </p>

      <h2>Your rights</h2>
      <p>You have the right to:</p>
      <ul>
        <li>Access the data we hold on you</li>
        <li>Correct inaccurate data</li>
        <li>Request deletion (subject to legal retention requirements)</li>
        <li>Withdraw consent to marketing</li>
      </ul>

      <h2>Security</h2>
      <p>
        Passwords are hashed with industry-standard algorithms. Transaction PINs are stored separately and hashed. All connections use HTTPS. We do NOT store your card number or bank credentials — those live only with our payment provider.
      </p>

      <h2>Contact</h2>
      <p>
        For privacy questions, contact <a href={`mailto:${site.email}`}>{site.email}</a>.
      </p>
    </>
  );
}
