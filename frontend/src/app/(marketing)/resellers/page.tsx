import { ResellerCTA, Stats, FinalCTA } from '@/components/marketing/Sections';

export const metadata = { title: 'Reseller Program' };

export default function Page() {
  return (
    <div className="pt-24">
      <div className="container-x pt-8 text-center">
        <h1 className="text-display-lg text-balance">
          Turn your phone into a real VTU business
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-surface-600 dark:text-surface-400">
          Join our reseller program and earn on every airtime, data, cable and electricity sale to your customers. No inventory. No overhead. Just profit.
        </p>
      </div>
      <ResellerCTA />
      <Stats />
      <FinalCTA />
    </div>
  );
}
