import { MarketingNav } from '../../components/marketing/MarketingNav';
import { MarketingFooter } from '../../components/marketing/MarketingFooter';

export default function LegalLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <MarketingNav />
      <main className="pt-24 pb-16">
        <div className="container-x max-w-3xl">
          <article className="prose prose-lg dark:prose-invert max-w-none">
            {children}
          </article>
        </div>
      </main>
      <MarketingFooter />
    </>
  );
}
