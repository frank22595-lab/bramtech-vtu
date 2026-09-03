import Link from 'next/link';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-white">
      <nav className="border-b p-4">
        <div className="max-w-3xl mx-auto flex justify-between">
          <Link href="/" className="text-sm">← Home</Link>
          <h1 className="font-bold">Privacy Policy</h1>
          <div className="w-12"></div>
        </div>
      </nav>
      <main className="max-w-3xl mx-auto p-8 prose">
        <h1>Privacy Policy</h1>
        <p><em>Last updated: September 2026</em></p>
        <p>Bram Technologies and Web Services respects your privacy.</p>
        <h2>What we collect</h2>
        <p>Phone, email, transactions, device info for security.</p>
        <h2>How we share</h2>
        <p>Only with payment providers, aggregators, and authorities when legally required.</p>
        <h2>Security</h2>
        <p>Passwords hashed, HTTPS everywhere, PIN hashed separately.</p>
        <h2>Contact</h2>
        <p>bright22595@gmail.com</p>
      </main>
    </div>
  );
}
