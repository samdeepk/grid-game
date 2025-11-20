import JoinPageClient from './JoinPageClient';

type JoinPageParams = {
  params: Promise<{ gameId: string }>;
};

export default async function JoinPage({ params }: JoinPageParams) {
  const { gameId } = await params;
  return <JoinPageClient gameId={gameId} />;
}
