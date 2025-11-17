import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getSession as apiGetSession, pollSession } from '../../utils/api';
import './waiting-room.scss';

interface WaitingRoomProps {
  sessionId: string;
}

export const WaitingRoom: React.FC<WaitingRoomProps> = ({ sessionId }) => {
  const [session, setSession] = useState<any>(null);
  const router = useRouter();

  useEffect(() => {
    (async () => {
      const s = await apiGetSession(sessionId);
      setSession(s);
    })();
    const unsub = pollSession(sessionId, (newS) => {
      setSession(newS);
    });
    return () => unsub();
  }, [sessionId]);

  if (!session) return <div>Session not found or expired.</div>;

  const joinLink = `${window.location.origin}/join/${sessionId}`;

  if (session.status === 'ACTIVE') {
    // Redirect to game
    router.push(`/game/${sessionId}`);
    return <div>Starting game...</div>;
  }

  return (
    <div className="waiting-room">
      <h2>Waiting for opponent</h2>
      <p>Share this link to invite a friend:</p>
      <pre className="join-link">{joinLink}</pre>
      <div>
        <h3>Players</h3>
        <ul>
          {session.players.map((p: any) => (
            <li key={p.id}>{p.icon ?? '🙂'} {p.name}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};
