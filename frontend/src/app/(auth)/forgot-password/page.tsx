import Link from 'next/link';
import { ArrowLeft, MessageCircle } from 'lucide-react';
import { site } from '@/lib/site';

export default function ForgotPasswordPage() {
  return (
    <div className="card-elevated animate-scale-in text-center">
      <h1 className="text-display-sm">Forgot your password?</h1>
      <p className="mt-3 text-surface-600 dark:text-surface-400">
        Password reset via email is coming soon. For now, please contact us on WhatsApp and we'll verify your identity and reset your password.
      </p>

      <a
        href={`https://wa.me/${site.whatsapp.replace(/\D/g, '')}?text=I%20forgot%20my%20BRAM%20password%20and%20need%20help%20resetting%20it.`}
        target="_blank"
        rel="noreferrer"
        className="btn-primary btn-lg mt-6 w-full"
      >
        <MessageCircle className="h-4 w-4" />
        WhatsApp Support
      </a>

      <Link href="/login" className="mt-4 inline-flex items-center gap-1 text-sm text-surface-600 hover:text-surface-900 dark:text-surface-400">
        <ArrowLeft className="h-4 w-4" /> Back to login
      </Link>
    </div>
  );
}
