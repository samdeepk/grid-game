'use client';

import { useRouter } from 'next/navigation';
import type { FC } from 'react';
import type { SessionListItem as SessionListItemType } from '../../utils/api';
import './session-list-item.scss';

interface SessionListItemProps {
  session: SessionListItemType;
  currentUserId: string;
}

export const SessionListItem: FC<SessionListItemProps> = ({ session, currentUserId }) => {
  const router = useRouter();

  const handleClick = () => {
    if (session.status === 'FINISHED') {
      router.push(`/game/${session.id}`);
    } else if (session.status === 'ACTIVE') {
      router.push(`/game/${session.id}`);
    } else {
      router.push(`/waiting/${session.id}`);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
  };

  const getStatusBadgeClass = () => {
    switch (session.status) {
      case 'WAITING':
        return 'status-waiting';
      case 'ACTIVE':
        return 'status-active';
      case 'FINISHED':
        return 'status-finished';
      default:
        return '';
    }
  };

  const getStatusLabel = () => {
    switch (session.status) {
      case 'WAITING':
        return 'Waiting';
      case 'ACTIVE':
        return 'Active';
      case 'FINISHED':
        return 'Finished';
      default:
        return session.status;
    }
  };

  return (
    <div className="session-list-item" onClick={handleClick}>
      <div className="session-icon">{session.gameIcon || '🎮'}</div>
      <div className="session-content">
        <div className="session-header">
          <span className={`status-badge ${getStatusBadgeClass()}`}>{getStatusLabel()}</span>
          <span className="session-date">{formatDate(session.createdAt)}</span>
        </div>
        <div className="session-players">
          {session.players.map((player, index) => (
            <span key={player.id} className="player-tag">
              {player.icon || '🙂'} {player.name}
              {player.id === currentUserId && <span className="you-badge">You</span>}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

