import React from 'react';
import { CellValue } from './types';

interface GameBoardProps {
  board: CellValue[][];
  onCellClick: (row: number, col: number) => void;
  disabled?: boolean;
  players?: Array<{ id: string | number; name?: string; icon?: string }>;
}

export const GameBoard: React.FC<GameBoardProps> = ({ board, onCellClick, disabled, players }) => {
  // Helper to get icon for a player ID
  const getPlayerIcon = (playerId: CellValue): string => {
    if (!playerId) return '';
    if (!players) return String(playerId);
    
    const player = players.find((p) => {
      if (typeof p === 'object' && p.id) {
        return p.id === playerId;
      }
      return p === playerId;
    });
    
    if (player && typeof player === 'object' && player.icon) {
      return player.icon;
    }
    // Fallback to a default icon if no icon found
    return '⚫';
  };

  return (
    <div className="ttt-board">
      {board.map((row, rowIdx) => (
        <div className="ttt-row" key={rowIdx}>
          {row.map((cell, colIdx) => (
            <button
              className="ttt-cell"
              key={colIdx}
              onClick={() => onCellClick(rowIdx, colIdx)}
              disabled={!!cell || disabled}
            >
              {getPlayerIcon(cell)}
            </button>
          ))}
        </div>
      ))}
    </div>
  );
};
