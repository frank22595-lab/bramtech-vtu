import Link from 'next/link';

export default function HomePage() {
  return (
    <div>
      {/* Nav */}
      <nav className="border-b bg-white sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-lg bg-brand-700 flex items-center justify-center text-white font-bold">B</div>
            <span className="font-bold text-xl">BRAM<span className="text-gold-500">.</span></span>
          </div>
          <div className="flex gap-3">
            <Link href="/auth/login" className="btn btn-outline">Log in</Link>
            <Link href="/auth/register" className="btn btn-primary">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-4 py-20 md:py-32 text-center">
        <div className="inline-block px-3 py-1 mb-6 rounded-full bg-brand-100 text-brand-800 text-xs font-semibold">
          Live — 24/7 service delivery
        </div>
        <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
          Airtime, data & bills.<br />
          <span className="text-brand-700">Delivered in seconds.</span>
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-8">
          Buy airtime, data, DStv, GOtv and pay electricity bills for any Nigerian network.
          One wallet. Instant delivery. Best prices.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link href="/auth/register" className="btn btn-primary btn-lg">Get Started Free →</Link>
          <Link href="#services" className="btn btn-outline btn-lg">See services</Link>
        </div>
      </section>

      {/* Services */}
      <section id="services" className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">Everything you need</h2>
          <p className="text-gray-600 text-center mb-14">Stop switching between apps. Buy any digital service instantly.</p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: 'Airtime', desc: 'All 4 networks', emoji: '📱' },
              { name: 'Data', desc: 'From ₦200', emoji: '📶' },
              { name: 'DStv / GOtv', desc: 'All packages', emoji: '📺' },
              { name: 'Electricity', desc: 'All DisCos', emoji: '⚡' },
              { name: 'Exam Pins', desc: 'Coming soon', emoji: '🎓' },
              { name: 'Betting', desc: 'Coming soon', emoji: '🎰' },
              { name: 'Bulk SMS', desc: 'Coming soon', emoji: '💬' },
              { name: 'Airtime→Cash', desc: 'Coming soon', emoji: '💵' },
            ].map((s) => (
              <div key={s.name} className="card text-center hover:shadow-lg transition">
                <div className="text-4xl mb-2">{s.emoji}</div>
                <h3 className="font-semibold">{s.name}</h3>
                <p className="text-sm text-gray-500 mt-1">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to start?</h2>
          <p className="text-gray-600 mb-8">Create your free account in 30 seconds.</p>
          <Link href="/auth/register" className="btn btn-primary btn-lg">Create Free Account →</Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white py-8">
        <div className="max-w-6xl mx-auto px-4 text-center text-sm text-gray-500">
          © {new Date().getFullYear()} Bram Technologies and Web Services. Okpanam, Delta State, Nigeria.
          <div className="mt-2 flex justify-center gap-4">
            <Link href="/legal/terms" className="hover:text-brand-700">Terms</Link>
            <Link href="/legal/privacy" className="hover:text-brand-700">Privacy</Link>
            <a href="https://wa.me/2348137925907" className="hover:text-brand-700">WhatsApp Support</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
