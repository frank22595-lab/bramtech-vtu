import { MessageCircle, Mail, MapPin, Phone } from 'lucide-react';
import { site } from '../lib/site';

export const metadata = { title: 'Contact us' };

export default function Page() {
  return (
    <div className="pt-24 pb-24">
      <div className="container-x max-w-3xl">
        <h1 className="text-display-lg">Get in touch</h1>
        <p className="mt-4 text-lg text-surface-600 dark:text-surface-400">
          We're a small team. Real humans answer every message.
        </p>

        <div className="mt-10 grid gap-4 md:grid-cols-2">
          <a href={`https://wa.me/${site.whatsapp.replace(/\D/g, '')}`} target="_blank" rel="noreferrer" className="card-interactive">
            <MessageCircle className="mb-3 h-6 w-6 text-primary-700" />
            <h3 className="font-bold">WhatsApp (fastest)</h3>
            <p className="mt-1 text-sm text-surface-600 dark:text-surface-400">
              Reply within 10 mins during business hours
            </p>
            <div className="mt-2 text-sm font-medium text-primary-700 dark:text-primary-400">{site.phone}</div>
          </a>

          <a href={`mailto:${site.email}`} className="card-interactive">
            <Mail className="mb-3 h-6 w-6 text-primary-700" />
            <h3 className="font-bold">Email</h3>
            <p className="mt-1 text-sm text-surface-600 dark:text-surface-400">
              For longer questions or documentation
            </p>
            <div className="mt-2 text-sm font-medium text-primary-700 dark:text-primary-400">{site.email}</div>
          </a>

          <div className="card">
            <Phone className="mb-3 h-6 w-6 text-primary-700" />
            <h3 className="font-bold">Phone</h3>
            <p className="mt-1 text-sm text-surface-600 dark:text-surface-400">
              Call between 9am – 6pm WAT weekdays
            </p>
            <div className="mt-2 text-sm font-medium">{site.phone}</div>
          </div>

          <div className="card">
            <MapPin className="mb-3 h-6 w-6 text-primary-700" />
            <h3 className="font-bold">Office</h3>
            <p className="mt-1 text-sm text-surface-600 dark:text-surface-400">
              Our home base
            </p>
            <div className="mt-2 text-sm font-medium">{site.address}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
