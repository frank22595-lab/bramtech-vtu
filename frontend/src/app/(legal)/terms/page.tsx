import { site } from '../../lib/site';

export const metadata = { title: 'Terms of Service' };

export default function Page() {
  return (
    <>
      <h1>Terms of Service</h1>
      <p><em>Last updated: August 2026</em></p>

      <p>
        These Terms of Service govern your use of {site.fullName} ("BRAM", "we", "us") operated by {site.company}, based in {site.address}. By creating an account or using our services, you agree to these terms.
      </p>

      <h2>1. Your account</h2>
      <p>
        You must provide accurate information when registering. You are responsible for keeping your login password and transaction PIN confidential. Any activity on your account is your responsibility.
      </p>

      <h2>2. Wallet & funds</h2>
      <p>
        Your wallet balance is held for the sole purpose of purchasing digital services on BRAM. Wallet funds are not a bank deposit and do not earn interest. Withdrawal back to bank accounts is not currently supported unless required by regulation.
      </p>

      <h2>3. Service delivery</h2>
      <p>
        We route your purchase requests through licensed third-party aggregators who deliver the actual service (airtime, data, subscription, etc.) directly to the recipient. We are responsible for reliable dispatch but not for the underlying network's delivery infrastructure.
      </p>

      <h2>4. Refunds</h2>
      <p>
        If a transaction fails, your wallet is automatically refunded within 30 seconds. See our Refund Policy for full details.
      </p>

      <h2>5. Reseller program</h2>
      <p>
        Reseller tier upgrades are one-time fees, non-refundable except in cases where we determine the tier was purchased in error. Reseller pricing discounts apply to future purchases only.
      </p>

      <h2>6. Prohibited use</h2>
      <p>You may not use BRAM for:</p>
      <ul>
        <li>Money laundering or fraud</li>
        <li>Purchasing airtime for unauthorised third parties without their consent</li>
        <li>Any activity that violates Nigerian law or the terms of our upstream providers</li>
      </ul>

      <h2>7. Termination</h2>
      <p>
        We may suspend or terminate your account if we detect fraudulent activity, violation of these terms, or as required by law. Wallet balances on suspended accounts will be reviewed case by case.
      </p>

      <h2>8. Limitation of liability</h2>
      <p>
        BRAM's liability for any claim is limited to the specific transaction amount in dispute. We are not liable for consequential damages such as missed calls, expired data, or loss of service.
      </p>

      <h2>9. Changes</h2>
      <p>
        We may update these terms. Continued use of BRAM after changes constitutes acceptance.
      </p>

      <h2>10. Contact</h2>
      <p>
        Questions? Reach us at <a href={`mailto:${site.email}`}>{site.email}</a> or WhatsApp {site.phone}.
      </p>
    </>
  );
}
