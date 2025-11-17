import React from 'react';
import { CellValue } from './types';

interface GameBoardProps {
  board: CellValue[][];
  onCellClick: (row: number, col: number) => void;
  disabled?: boolean;
}

export const GameBoard: React.FC<GameBoardProps> = ({ board, onCellClick, disabled }) => (
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
            {cell ?? ''}
          </button>
        ))}
      </div>
    ))}
  </div>
);
