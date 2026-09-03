import Link from 'next/link';

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-white">
      <nav className="border-b p-4">
        <div className="max-w-3xl mx-auto flex justify-between">
          <Link href="/" className="text-sm">← Home</Link>
          <h1 className="font-bold">Terms of Service</h1>
          <div className="w-12"></div>
        </div>
      </nav>
      <main className="max-w-3xl mx-auto p-8 prose">
        <h1>Terms of Service</h1>
        <p><em>Last updated: September 2026</em></p>
        <p>These terms govern your use of BRAM Data & Utilities, operated by Bram Technologies and Web Services, Okpanam, Delta State, Nigeria.</p>
        <h2>Account</h2>
        <p>You must provide accurate registration information and keep your PIN confidential.</p>
        <h2>Wallet</h2>
        <p>Wallet funds are held for purchasing services only. Not a bank deposit.</p>
        <h2>Refunds</h2>
        <p>Failed transactions auto-refund within 30 seconds.</p>
        <h2>Contact</h2>
        <p>Email bright22595@gmail.com or WhatsApp +234 813 792 5907.</p>
      </main>
    </div>
  );
}
