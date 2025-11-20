import React from 'react';
import { Player, PlayerId } from '../../types/game';

interface GameStatusProps {
  currentTurn: PlayerId | null;
  winner: PlayerId | null;
  draw?: boolean;
  players: Player[];
}

export const GameStatus: React.FC<GameStatusProps> = ({ currentTurn, winner, draw, players }) => {
  const getPlayerName = (id: PlayerId | null) => {
    if (!id) return '';
    const p = players.find((player) => player.id === id);
    return p ? p.name : id;
  };

  if (winner) return <div className="ttt-status">Winner: {getPlayerName(winner)}</div>;
  if (draw) return <div className="ttt-status">Draw!</div>;
  
  return <div className="ttt-status">Current turn: {getPlayerName(currentTurn)}</div>;
};
