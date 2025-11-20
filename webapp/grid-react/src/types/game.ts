export type PlayerId = string;

export interface Player {
  id: PlayerId;
  name: string;
  icon?: string;
}

export type CellValue = PlayerId | null;

export interface Move {
  playerId: PlayerId;
  row: number;
  col: number;
}

export interface GameSession {
  id: string;
  players: Player[];
  status: 'WAITING' | 'ACTIVE' | 'FINISHED';
  currentTurn?: PlayerId | null;
  board: CellValue[][];
  moves: Move[];
  winner?: PlayerId | null;
  draw?: boolean;
  createdAt?: string;
}

export interface GameState {
  board: CellValue[][];
  currentTurn: PlayerId | null;
  players: Player[];
  winner: PlayerId | null;
  draw: boolean;
  status: 'WAITING' | 'ACTIVE' | 'FINISHED';
}

