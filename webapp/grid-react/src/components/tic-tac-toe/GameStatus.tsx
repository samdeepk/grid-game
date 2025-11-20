import React from 'react';
import { PlayerId } from './types';

interface GameStatusProps {
  currentTurn: PlayerId;
  winner: PlayerId | null;
  draw: boolean;
  players?: Array<PlayerId | { id: PlayerId; name?: string; icon?: string }>;
}

export const GameStatus: React.FC<GameStatusProps> = ({ currentTurn, winner, draw, players }) => {
  // Helper to get player display (icon + name)
  const getPlayerDisplay = (playerId: PlayerId | null): string => {
    if (!playerId) return '';
    if (!players) return String(playerId);
    
    const matched = players.find((p) => {
      if (typeof p === 'string' || typeof p === 'number') {
        return p === playerId;
      }
      return (p as any).id === playerId;
    });
    
    if (matched && typeof matched !== 'string' && typeof matched !== 'number') {
      const player = matched as any;
      const icon = player.icon ? `${player.icon} ` : '';
      const name = player.name ?? String(player.id);
      return `${icon}${name}`;
    }
    
    return String(playerId);
  };

  if (winner) {
    const winnerDisplay = getPlayerDisplay(winner);
    return <div className="ttt-status">Winner: {winnerDisplay}</div>;
  }
  if (draw) return <div className="ttt-status">Draw!</div>;
  
  const currentDisplay = getPlayerDisplay(currentTurn);
  return <div className="ttt-status">Current turn: {currentDisplay}</div>;
};
