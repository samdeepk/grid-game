'use client';

import type { FC } from 'react';
import { useState, useEffect } from 'react';
import { listSessions, type SessionListItem } from '../../utils/api';
import { getUserId } from '../../utils/userStorage';
import { SessionListItem as SessionListItemComponent } from './session-list-item';
import './game-list.scss';

interface GamelistProps {
  onOpenCreateGameModal?: () => void;
  onOpenUserNameModal?: () => void;
}

const Gamelist: FC<GamelistProps> = ({ onOpenCreateGameModal }) => {
  const [sessions, setSessions] = useState<SessionListItem[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const userId = getUserId();

  useEffect(() => {
    const fetchSessions = async () => {
      if (!userId) {
        setSessions([]);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const response = await listSessions({ hostId: userId, limit: 50 });
        // Filter to show only sessions where user is a player (host or guest)
        const userSessions = response.items.filter(
          (session) =>
            session.host.id === userId ||
            session.players.some((player) => player.id === userId)
        );
        setSessions(userSessions);
      } catch (err) {
        console.error('Error fetching sessions:', err);
        setError(err instanceof Error ? err.message : 'Failed to load games');
        setSessions([]);
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, [userId]);

  const hasSessions = Boolean(sessions && sessions.length > 0);

  if (loading) {
    return (
      <div className="gamelist-wrapper" data-testid="game-list">
        <div className="gamelist-loading">Loading games...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="gamelist-wrapper" data-testid="game-list">
        <div className="gamelist-error">
          <p>{error}</p>
          <button
            onClick={() => {
              setLoading(true);
              setError(null);
              const fetchSessions = async () => {
                if (!userId) {
                  setSessions([]);
                  setLoading(false);
                  return;
                }
                try {
                  const response = await listSessions({ hostId: userId, limit: 50 });
                  const userSessions = response.items.filter(
                    (session) =>
                      session.host.id === userId ||
                      session.players.some((player) => player.id === userId)
                  );
                  setSessions(userSessions);
                } catch (err) {
                  setError(err instanceof Error ? err.message : 'Failed to load games');
                  setSessions([]);
                } finally {
                  setLoading(false);
                }
              };
              fetchSessions();
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="gamelist-wrapper" data-testid="game-list">
      {hasSessions && userId && (
        <div className="gamelist-items">
          {sessions!.map((session) => (
            <SessionListItemComponent key={session.id} session={session} currentUserId={userId} />
          ))}
        </div>
      )}
      {!hasSessions && (
        <div className="gamelist-empty-state">
          <div>No games yet</div>
          <div>
            <button onClick={() => onOpenCreateGameModal && onOpenCreateGameModal()}>
              Start Playing
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Gamelist;
