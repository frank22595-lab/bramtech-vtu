import { FAQ } from '@/components/marketing/Sections';

export const metadata = { title: 'FAQ' };

export default function Page() {
  return (
    <div className="pt-24">
      <div className="container-x pt-8 text-center">
        <h1 className="text-display-lg">Questions? We've got answers.</h1>
      </div>
      <FAQ />
    </div>
  );
}
