import { HowItWorks, Services, FinalCTA } from '../../components/marketing/Sections';

export const metadata = { title: 'How it works' };

export default function Page() {
  return (
    <div className="pt-24">
      <div className="container-x pt-8 text-center">
        <h1 className="text-display-lg text-balance">How BRAM works</h1>
        <p className="mx-auto mt-4 max-w-xl text-lg text-surface-600 dark:text-surface-400">
          Three steps to fast, reliable digital services.
        </p>
      </div>
      <HowItWorks />
      <Services />
      <FinalCTA />
    </div>
  );
}
