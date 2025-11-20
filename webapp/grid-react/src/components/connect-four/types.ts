import { Player, PlayerId } from '../../types/game';

export type CellValue = PlayerId | null;

export interface GameState {
  board: CellValue[][]; // 6x7 grid
  currentTurn: PlayerId;
  players: Player[];
  winner: PlayerId | null;
  draw: boolean;
}

export interface Move {
  row: number;
  col: number;
  player: PlayerId;
}

