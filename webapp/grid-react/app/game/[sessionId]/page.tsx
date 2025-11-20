'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getSession as apiGetSession, type Session } from '../../../src/utils/api';
import { TicTacToe } from '../../../src/components/tic-tac-toe';
import { ConnectFour } from '../../../src/components/connect-four';

export default function GamePage({ params }: { params: { sessionId: string } }) {
  const { sessionId } = params;
  const router = useRouter();
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const s = await apiGetSession(sessionId);
        if (!s) {
          alert('Game session not found.');
          router.push('/');
          return;
        }
        setSession(s);
      } catch (error) {
        console.error('Error fetching session:', error);
        alert('Failed to load game session.');
        router.push('/');
      } finally {
        setLoading(false);
      }
    };
    checkSession();
  }, [sessionId, router]);

  if (loading) return <div>Loading...</div>;
  if (!session) return null;

  const gameType = session.gameType || 'tic_tac_toe';

  return (
    <div>
      <h1>Game {sessionId}</h1>
      {gameType === 'connect_four' ? (
        <ConnectFour sessionId={sessionId} />
      ) : (
        <TicTacToe sessionId={sessionId} />
      )}
    </div>
  );
}
