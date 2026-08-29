import { Hero } from '@/components/marketing/Hero';
import { Services, HowItWorks, Stats, Features, ResellerCTA, FAQ, FinalCTA } from '@/components/marketing/Sections';

export default function HomePage() {
  return (
    <>
      <Hero />
      <Services />
      <HowItWorks />
      <Stats />
      <Features />
      <ResellerCTA />
      <FAQ />
      <FinalCTA />
    </>
  );
}
