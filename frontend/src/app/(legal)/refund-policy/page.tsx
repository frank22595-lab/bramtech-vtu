import { site } from '../lib/site';

export const metadata = { title: 'Refund Policy' };

export default function Page() {
  return (
    <>
      <h1>Refund Policy</h1>
      <p><em>Last updated: August 2026</em></p>

      <h2>Automatic refunds</h2>
      <p>
        If a transaction fails at the aggregator or provider level, your wallet is automatically refunded within 30 seconds. This is our commitment aligned with CBN's payment service SLA.
      </p>

      <h2>What counts as "failed"</h2>
      <ul>
        <li>Aggregator returns a failure status</li>
        <li>Aggregator does not respond within 5 minutes (auto-refunded as safety net)</li>
        <li>Recipient details are invalid (wrong phone / meter / smartcard number)</li>
      </ul>

      <h2>What does NOT qualify for refund</h2>
      <ul>
        <li>Successful transactions where you entered the wrong recipient</li>
        <li>Change of mind after successful delivery</li>
        <li>Reseller tier upgrade fees (see Terms)</li>
      </ul>

      <h2>Disputed transactions</h2>
      <p>
        If you believe a transaction was charged but not delivered, contact us within 7 days with the transaction reference. We investigate every case with our aggregator partners and refund if the aggregator confirms non-delivery.
      </p>

      <h2>Wallet withdrawals</h2>
      <p>
        Wallet balance is intended for buying services, not as a bank deposit. Withdrawal back to your bank account is available only in specific cases (account closure, unresolved service issues) and processed within 5 business days.
      </p>

      <h2>Contact for disputes</h2>
      <p>
        Email <a href={`mailto:${site.email}`}>{site.email}</a> or WhatsApp {site.phone} with your transaction reference (starts with "BRT-"). We aim to resolve every case within 24 hours.
      </p>
    </>
  );
}
