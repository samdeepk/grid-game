import React from 'react';
import { CellValue } from './types';
import { getPlayerColor } from '../../utils/colors';

interface GameBoardProps {
  board: CellValue[][];
  onCellClick: (row: number, col: number) => void;
  disabled?: boolean;
  players?: Array<{ id: string | number; name?: string; icon?: string } | string | number>;
}

export const GameBoard: React.FC<GameBoardProps> = ({ board, onCellClick, disabled, players }) => {
  // Helper to get icon for a player ID
  const getPlayerIcon = (playerId: CellValue): string => {
    if (!playerId) return '';
    if (!players) return String(playerId);
    
    const playerIndex = players.findIndex((p) => {
      if (typeof p === 'object' && p !== null && 'id' in p) {
        return p.id === playerId;
      }
      return p === playerId;
    });

    if (playerIndex === -1) return String(playerId);

    const player = players[playerIndex];
    
    if (typeof player === 'object' && player !== null && 'icon' in player && player.icon) {
      return player.icon;
    }

    // Default modern icons based on index
    if (playerIndex === 0) return '✕';
    if (playerIndex === 1) return '◯';
    
    return ['△', '□', '◇'][playerIndex - 2] || String(playerId).substring(0, 1);
  };

  // Helper to get color style for player
  const getPlayerStyle = (playerId: CellValue) => {
    if (!playerId || !players) return {};
    
    const player = players.find((p) => {
      if (typeof p === 'object' && p !== null && 'id' in p) {
        return p.id === playerId;
      }
      return p === playerId;
    });

    if (!player) return {};

    const id = typeof player === 'object' && 'id' in player ? String(player.id) : String(player);
    const name = typeof player === 'object' && 'name' in player ? player.name || id : id;
    
    const color = getPlayerColor(name);
    
    return { color, backgroundColor: color };
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
              style={getPlayerStyle(cell)}
              aria-label={`Cell ${rowIdx},${colIdx} ${cell ? 'occupied' : 'empty'}`}
            >
              {getPlayerIcon(cell)}
            </button>
          ))}
        </div>
      ))}
    </div>
  );
};
