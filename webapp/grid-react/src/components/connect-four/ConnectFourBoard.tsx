import React, { useState } from 'react';
import { CellValue } from './types';
import { Player } from '../../types/game';

interface ConnectFourBoardProps {
  board: CellValue[][];
  onColumnClick: (col: number) => void;
  disabled?: boolean;
  players?: Player[];
}

export const ConnectFourBoard: React.FC<ConnectFourBoardProps> = ({ 
  board, 
  onColumnClick, 
  disabled, 
  players 
}) => {
  const [hoveredColumn, setHoveredColumn] = useState<number | null>(null);
  // Helper to get icon for a player ID
  const getPlayerIcon = (playerId: CellValue): string => {
    if (!playerId) return '';
    if (!players) return String(playerId);
    
    const player = players.find((p) => p.id === playerId);
    
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
        {Array.from({ length: numCols }, (_, colIdx) => {
          const isFull = isColumnFull(colIdx);
          const isHovered = hoveredColumn === colIdx && !isFull && !disabled;
          
          return (
            <button
              key={colIdx}
              className={`c4-column-header ${isFull ? 'full' : ''} ${isHovered ? 'hovered' : ''}`}
              onClick={() => !isFull && !disabled && onColumnClick(colIdx)}
              onMouseEnter={() => !isFull && !disabled && setHoveredColumn(colIdx)}
              onMouseLeave={() => setHoveredColumn(null)}
              disabled={isFull || disabled}
              type="button"
              title={isFull ? 'Column is full' : `Drop piece in column ${colIdx + 1}`}
            >
              <span className="c4-column-number">{colIdx + 1}</span>
              <span className="c4-column-arrow">↓</span>
            </button>
          );
        })}
      </div>
      
      {/* Game board - rendered as columns */}
      <div className="c4-board">
        {Array.from({ length: numCols }, (_, colIdx) => (
          <div className="c4-column" key={colIdx}>
            {board.map((row, rowIdx) => {
              const cell = row[colIdx];
              const dropRow = findDropRow(colIdx);
              const isDropPosition = dropRow === rowIdx && !isColumnFull(colIdx);
              const isHoveredDrop = hoveredColumn === colIdx && dropRow === rowIdx && !isColumnFull(colIdx) && !disabled;
              
              return (
                <div
                  key={rowIdx}
                  className={`c4-cell ${isDropPosition ? 'drop-position' : ''} ${isHoveredDrop ? 'hovered-drop' : ''} ${hoveredColumn === colIdx && !isColumnFull(colIdx) && !disabled ? 'column-hovered' : ''}`}
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

