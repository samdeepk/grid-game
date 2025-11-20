// Shared types for TicTacToe state, moves, and players

export type PlayerId = number | string;

export type CellValue = PlayerId | null;

export interface GameState {
  board: CellValue[][]; // 3x3 grid
  currentTurn: PlayerId;
  players: Array<PlayerId | { id: PlayerId; icon?: string; name?: string }>;
  winner: PlayerId | null;
  draw: boolean;
}

export interface Move {
  row: number;
  col: number;
  player: PlayerId;
}
