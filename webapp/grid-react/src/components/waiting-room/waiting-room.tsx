import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useGameSession } from '../../hooks/useGameSession';
import { useToast } from '../../context/ToastContext';
import './waiting-room.scss';

interface WaitingRoomProps {
  sessionId: string;
}

export const WaitingRoom: React.FC<WaitingRoomProps> = ({ sessionId }) => {
  const router = useRouter();
  const { session, loading, error } = useGameSession(sessionId);
  const [joinLink, setJoinLink] = useState('');
  const { showToast } = useToast();

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setJoinLink(`${window.location.origin}/join/${sessionId}`);
    }
  }, [sessionId]);

  // Redirect to game when active
  useEffect(() => {
    if (session?.status === 'ACTIVE') {
      showToast('Game started!', 'success');
      router.push(`/game/${sessionId}`);
    }
  }, [session?.status, sessionId, router, showToast]);

  if (loading) return <div className="waiting-loading">Loading waiting room...</div>;
  
  if (error) {
    return <div className="waiting-error">{error}</div>;
  }

  if (!session) return <div className="waiting-error">Session not found or expired.</div>;

  const copyLink = () => {
    navigator.clipboard.writeText(joinLink);
    showToast('Link copied to clipboard!', 'info');
  };

  return (
    <div className="waiting-room">
      <h2>Waiting for opponent</h2>
      <p>Share this link to invite a friend:</p>
      <div className="link-container">
        <pre className="join-link">{joinLink}</pre>
        <button onClick={copyLink} className="copy-button">Copy</button>
      </div>
      
      <div className="players-list">
        <h3>Players Joined ({session.players.length}/2)</h3>
        <ul>
          {session.players.map((p) => (
            <li key={p.id} className="player-item">
              <span className="player-icon">{p.icon ?? '🙂'}</span>
              <span className="player-name">{p.name}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
