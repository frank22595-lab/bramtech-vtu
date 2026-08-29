import Link from 'next/link';
import { Instagram, Twitter, Facebook, Linkedin, MessageCircle } from 'lucide-react';
import { Logo } from '@/components/Logo';
import { site } from '@/lib/site';

export function MarketingFooter() {
  return (
    <footer className="border-t border-surface-200 bg-surface-50 dark:border-surface-800 dark:bg-surface-950">
      <div className="container-x py-12 md:py-16">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-5">
          <div className="col-span-2 md:col-span-2">
            <Logo />
            <p className="mt-4 max-w-xs text-sm text-surface-600 dark:text-surface-400">
              {site.description}
            </p>
            <div className="mt-6 flex gap-3">
              <a href={`https://wa.me/${site.whatsapp.replace(/\D/g, '')}`}
                 target="_blank" rel="noreferrer"
                 className="rounded-full bg-primary-100 p-2 text-primary-700 hover:bg-primary-200 dark:bg-primary-900/30 dark:text-primary-400"
                 aria-label="WhatsApp">
                <MessageCircle className="h-4 w-4" />
              </a>
              <a href={site.socials.twitter} target="_blank" rel="noreferrer"
                 className="rounded-full bg-surface-100 p-2 text-surface-600 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-400"
                 aria-label="Twitter">
                <Twitter className="h-4 w-4" />
              </a>
              <a href={site.socials.instagram} target="_blank" rel="noreferrer"
                 className="rounded-full bg-surface-100 p-2 text-surface-600 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-400"
                 aria-label="Instagram">
                <Instagram className="h-4 w-4" />
              </a>
              <a href={site.socials.facebook} target="_blank" rel="noreferrer"
                 className="rounded-full bg-surface-100 p-2 text-surface-600 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-400"
                 aria-label="Facebook">
                <Facebook className="h-4 w-4" />
              </a>
              <a href={site.socials.linkedin} target="_blank" rel="noreferrer"
                 className="rounded-full bg-surface-100 p-2 text-surface-600 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-400"
                 aria-label="LinkedIn">
                <Linkedin className="h-4 w-4" />
              </a>
            </div>
          </div>

          <FooterColumn title="Product" items={site.nav.footer.product} />
          <FooterColumn title="Company" items={site.nav.footer.company} />
          <FooterColumn title="Legal" items={site.nav.footer.legal} />
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-surface-200 pt-8 md:flex-row dark:border-surface-800">
          <div className="text-xs text-surface-500">
            © {new Date().getFullYear()} {site.company}. All rights reserved.
          </div>
          <div className="text-xs text-surface-500">
            Built with care in {site.address}
          </div>
        </div>
      </div>
    </footer>
  );
}

function FooterColumn({ title, items }: { title: string; items: readonly { label: string; href: string }[] }) {
  return (
    <div>
      <h3 className="mb-3 text-sm font-semibold text-surface-900 dark:text-surface-100">{title}</h3>
      <ul className="space-y-2">
        {items.map((i) => (
          <li key={i.href}>
            <Link href={i.href} className="text-sm text-surface-600 hover:text-primary-700 dark:text-surface-400 dark:hover:text-primary-400">
              {i.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
