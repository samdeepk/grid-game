import React from 'react';
import { CellValue } from './types';

interface CellProps {
  value: CellValue;
  onClick: () => void;
  disabled?: boolean;
}

export const Cell: React.FC<CellProps> = ({ value, onClick, disabled }) => (
  <button className="ttt-cell" onClick={onClick} disabled={!!value || disabled}>
    {value ?? ''}
  </button>
);
