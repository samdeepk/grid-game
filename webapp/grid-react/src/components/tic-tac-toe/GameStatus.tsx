import React from 'react';
import { PlayerId } from './types';

interface GameStatusProps {
  currentTurn: PlayerId;
  winner: PlayerId | null;
  draw: boolean;
  players?: Array<PlayerId | { id: PlayerId; name?: string; icon?: string }>;
}

export const GameStatus: React.FC<GameStatusProps> = ({ currentTurn, winner, draw, players }) => {
  let currentName: string | null = null;
  if (players) {
    const matched = players.find((p) => (typeof p === 'string' ? p === currentTurn : (p as any).id === currentTurn));
    if (matched && typeof matched !== 'string' && typeof matched !== 'number') {
      currentName = (matched as any).name ?? String((matched as any).id);
    }
  }
  if (winner) return <div className="ttt-status">Winner: {winner}</div>;
  if (draw) return <div className="ttt-status">Draw!</div>;
  return <div className="ttt-status">Current turn: {currentName ?? currentTurn}</div>;
};
