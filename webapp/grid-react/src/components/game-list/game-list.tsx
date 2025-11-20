'use client';

import type { FC } from 'react';
import { SessionListItem as SessionListItemComponent } from './session-list-item';
import { useSessionList } from '../../hooks/useSessionList';
import { useUser } from '../../context/UserContext';
import './game-list.scss';

interface GamelistProps {
  onOpenCreateGameModal?: () => void;
  onOpenUserNameModal?: () => void;
}

const Gamelist: FC<GamelistProps> = ({ onOpenCreateGameModal }) => {
  const { user } = useUser();
  const { sessions, loading, error, refresh } = useSessionList(user?.id ?? null);

  const hasSessions = sessions.length > 0;

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
          <button onClick={refresh}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="gamelist-wrapper" data-testid="game-list">
      {hasSessions && user?.id && (
        <div className="gamelist-items">
          {sessions.map((session) => (
            <SessionListItemComponent key={session.id} session={session} currentUserId={user.id} />
          ))}
        </div>
      )}
      {!hasSessions && (
        <div className="gamelist-empty-state">
          <div>No games yet</div>
          <div>
            <button onClick={() => onOpenCreateGameModal?.()}>
              Start Playing
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Gamelist;
