import GamePageClient from './GamePageClient';

type GamePageParams = {
  params: Promise<{ sessionId: string }>;
};

export default async function GamePage({ params }: GamePageParams) {
  const { sessionId } = await params;
  return <GamePageClient sessionId={sessionId} />;
}
