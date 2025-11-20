import React from 'react';
import { CellValue } from './types';

interface ConnectFourBoardProps {
  board: CellValue[][];
  onColumnClick: (col: number) => void;
  disabled?: boolean;
  players?: Array<{ id: string | number; name?: string; icon?: string }>;
}

export const ConnectFourBoard: React.FC<ConnectFourBoardProps> = ({ 
  board, 
  onColumnClick, 
  disabled, 
  players 
}) => {
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

  // Check if a column is full
  const isColumnFull = (col: number): boolean => {
    return board[0][col] !== null;
  };

  // Find the drop row for a column (lowest empty row)
  const findDropRow = (col: number): number | null => {
    for (let row = board.length - 1; row >= 0; row--) {
      if (board[row][col] === null) {
        return row;
      }
    }
    return null;
  };

  const numCols = board[0]?.length || 7;

  return (
    <div className="c4-board-container">
      {/* Column headers - clickable to drop pieces */}
      <div className="c4-column-headers">
        {Array.from({ length: numCols }, (_, colIdx) => (
          <button
            key={colIdx}
            className={`c4-column-header ${isColumnFull(colIdx) ? 'full' : ''}`}
            onClick={() => !isColumnFull(colIdx) && !disabled && onColumnClick(colIdx)}
            disabled={isColumnFull(colIdx) || disabled}
            type="button"
            title={isColumnFull(colIdx) ? 'Column is full' : `Drop piece in column ${colIdx + 1}`}
          >
            ↓
          </button>
        ))}
      </div>
      
      {/* Game board */}
      <div className="c4-board">
        {board.map((row, rowIdx) => (
          <div className="c4-row" key={rowIdx}>
            {row.map((cell, colIdx) => {
              const dropRow = findDropRow(colIdx);
              const isDropPosition = dropRow === rowIdx && !isColumnFull(colIdx);
              
              return (
                <div
                  key={colIdx}
                  className={`c4-cell ${isDropPosition ? 'drop-position' : ''}`}
                >
                  {cell ? (
                    <div className="c4-piece">{getPlayerIcon(cell)}</div>
                  ) : (
                    <div className="c4-empty" />
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
};

