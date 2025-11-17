import React from 'react';
import { PlayerId } from './types';

interface PlayerInfoProps {
  players: Array<{ id: PlayerId; name?: string; icon?: string }> | PlayerId[];
  currentTurn: PlayerId;
}

export const PlayerInfo: React.FC<PlayerInfoProps> = ({ players, currentTurn }) => (
  <div className="ttt-players">
    {players.map((p: any) => (
      <span key={p.id ?? p} className={p.id === currentTurn || p === currentTurn ? 'ttt-player-active' : ''}>
        {p.icon ? `${p.icon} ` : ''}{p.name ?? p.id ?? p}
      </span>
    ))}
  </div>
);
