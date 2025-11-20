import WaitingPageClient from './WaitingPageClient';

type WaitingPageParams = {
  params: Promise<{ sessionId: string }>;
};

export default async function WaitingHostPage({ params }: WaitingPageParams) {
  const { sessionId } = await params;
  return <WaitingPageClient sessionId={sessionId} />;
}
