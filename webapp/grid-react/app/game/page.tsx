'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { getSession as apiGetSession, type Session } from '../../src/utils/api';
import { TicTacToe } from '../../src/components/tic-tac-toe';
import { ConnectFour } from '../../src/components/connect-four';

function GameContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('id');
  const router = useRouter();
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionId) {
      router.push('/');
      return;
    }

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
  if (!session || !sessionId) return null;

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

export default function GamePage() {
  return (
    <Suspense fallback={<div>Loading game...</div>}>
      <GameContent />
    </Suspense>
  );
}

