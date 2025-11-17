'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getSession as apiGetSession } from '../../../src/utils/api';
import { TicTacToe } from '../../../src/components/tic-tac-toe';

export default function GamePage({ params }: { params: { sessionId: string } }) {
  const { sessionId } = params;
  const router = useRouter();
  const [sessionExists, setSessionExists] = useState<boolean | null>(null);

  useEffect(() => {
    const checkSession = async () => {
        const s = await apiGetSession(sessionId);
        if (!s) {
        alert('Game session not found.');
        router.push('/');
        return;
        }
        setSessionExists(true);
    }
    checkSession();
  }, [sessionId]);

  if (sessionExists === null) return <div>Loading...</div>;

  return (
    <div>
      <h1>Game {sessionId}</h1>
      <TicTacToe sessionId={sessionId} />
    </div>
  );
}
