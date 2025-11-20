import React from 'react';
import { Player, PlayerId } from '../../types/game';

interface PlayerInfoProps {
  players: Player[];
  currentTurn: PlayerId | null;
}

export const PlayerInfo: React.FC<PlayerInfoProps> = ({ players, currentTurn }) => (
  <div className="ttt-players">
    {players.map((p) => (
      <span key={p.id} className={p.id === currentTurn ? 'ttt-player-active' : ''}>
        {p.icon ? `${p.icon} ` : ''}{p.name || p.id}
      </span>
    ))}
  </div>
);
