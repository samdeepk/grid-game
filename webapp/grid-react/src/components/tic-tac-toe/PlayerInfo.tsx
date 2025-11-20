import React from 'react';
import { Player, PlayerId } from '../../types/game';
import { getPlayerColor } from '../../utils/colors';

interface PlayerInfoProps {
  players: Player[];
  currentTurn: PlayerId | null;
}

export const PlayerInfo: React.FC<PlayerInfoProps> = ({ players, currentTurn }) => {
  const getPlayerIcon = (player: Player, index: number) => {
    if (player.icon) return player.icon;
    if (index === 0) return '✕';
    if (index === 1) return '◯';
    return '⚫';
  };

  const getPlayerStyle = (player: Player) => {
    const color = getPlayerColor(player.name || player.id);
    return { color };
  };

  return (
    <>
      {players.map((p, idx) => {
        const isActive = p.id === currentTurn;
        const style = getPlayerStyle(p);
        
        return (
          <div 
            key={p.id} 
            className={`ttt-player-info ${isActive ? 'active' : 'inactive'}`}
            style={isActive ? style : {}}
          >
            <span className="player-icon" style={style}>{getPlayerIcon(p, idx)}</span>
            <span className="player-name" style={style}>{p.name || p.id}</span>
          </div>
        );
      })}
    </>
  );
};
