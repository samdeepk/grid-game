// Lightweight in-browser session service to mock server state.
// Designed so it can be swapped with a real HTTP/WebSocket API later.

import { PlayerId } from '../components/tic-tac-toe/types';

export type Player = {
  id: string;
  name: string;
  icon?: string;
};

export type Move = {
  playerId: string;
  row: number;
  col: number;
};

export type Session = {
  id: string;
  players: Player[];
  status: 'WAITING' | 'ACTIVE' | 'FINISHED';
  createdAt: string;
  currentTurn?: string | null;
  board: (string | null)[][]; // player ids or null
  moves: Move[];
  winner?: string | null;
  draw?: boolean;
};

const KEY_PREFIX = 'grid-game-session-';

function makeKey(sessionId: string) {
  return KEY_PREFIX + sessionId;
}

function generateId() {
  return (typeof crypto !== 'undefined' && (crypto as any).randomUUID
    ? (crypto as any).randomUUID()
    : Math.random().toString(36).slice(2, 9));
}

function emptyBoard() {
  return Array.from({ length: 3 }, () => Array(3).fill(null));
}

function saveSession(session: Session) {
  localStorage.setItem(makeKey(session.id), JSON.stringify(session));
  // Trigger storage event in other tabs by setting a 'last-update' key
  localStorage.setItem(`${makeKey(session.id)}-updatedAt`, new Date().toISOString());
}

function loadSession(sessionId: string): Session | null {
  const txt = localStorage.getItem(makeKey(sessionId));
  if (!txt) return null;
  try {
    return JSON.parse(txt) as Session;
  } catch (e) {
    return null;
  }
}

export function createSession(host: Player) {
  const id = generateId();
  const s: Session = {
    id,
    players: [host],
    status: 'WAITING',
    createdAt: new Date().toISOString(),
    currentTurn: null,
    board: emptyBoard(),
    moves: [],
    winner: null,
    draw: false,
  };
  saveSession(s);
  return s;
}

export function getSession(sessionId: string) {
  return loadSession(sessionId);
}

export function joinSession(sessionId: string, player: Player): Session | null {
  const s = loadSession(sessionId);
  if (!s) return null;
  // Already joined
  if (s.players.find((p) => p.id === player.id)) return s;
  if (s.players.length >= 2) return s; // can't join full game
  s.players.push(player);
  s.status = 'ACTIVE';
  // Randomly pick a current turn: first player
  s.currentTurn = s.players[0].id;
  saveSession(s);
  return s;
}

function checkWinner(board: (string | null)[][], playerId: string | null) {
  if (!playerId) return false;
  // rows
  for (let r = 0; r < 3; r++) {
    if (board[r].every((c) => c === playerId)) return true;
  }
  // cols
  for (let c = 0; c < 3; c++) {
    if (board.every((row) => row[c] === playerId)) return true;
  }
  // diag
  if ([0, 1, 2].every((i) => board[i][i] === playerId)) return true;
  if ([0, 1, 2].every((i) => board[i][2 - i] === playerId)) return true;
  return false;
}

export function makeMove(sessionId: string, playerId: string, row: number, col: number) {
  const s = loadSession(sessionId);
  if (!s) return { ok: false, message: 'session not found' };
  if (s.status !== 'ACTIVE') return { ok: false, message: 'game not active' };
  if (s.currentTurn !== playerId) return { ok: false, message: 'not your turn' };
  if (s.board[row][col] !== null) return { ok: false, message: 'cell occupied' };
  s.board[row][col] = playerId;
  s.moves.push({ playerId, row, col });
  // check winner
  const isWinner = checkWinner(s.board, playerId);
  if (isWinner) {
    s.status = 'FINISHED';
    s.winner = playerId;
  } else if (s.moves.length >= 9) {
    s.status = 'FINISHED';
    s.draw = true;
  } else {
    // switch turn
    const other = s.players.find((p) => p.id !== playerId);
    s.currentTurn = other ? other.id : s.currentTurn;
  }
  saveSession(s);
  return { ok: true, session: s };
}

export function watchSession(sessionId: string, cb: (s: Session | null) => void) {
  // Listen to storage events in other tabs
  const handler = (ev: StorageEvent) => {
    if (!ev.key) return;
    if (ev.key.startsWith(makeKey(sessionId))) {
      cb(loadSession(sessionId));
    }
  };
  window.addEventListener('storage', handler);

  // Also call periodically in same tab
  let last = JSON.stringify(loadSession(sessionId));
  const interval = window.setInterval(() => {
    const cur = JSON.stringify(loadSession(sessionId));
    if (cur !== last) {
      last = cur;
      cb(loadSession(sessionId));
    }
  }, 300);

  // initial
  cb(loadSession(sessionId));

  return () => {
    window.removeEventListener('storage', handler);
    clearInterval(interval);
  };
}
