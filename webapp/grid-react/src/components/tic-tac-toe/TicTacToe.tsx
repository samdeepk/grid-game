import React, { useEffect, useState } from 'react';
import { getSession as apiGetSession, pollSession, makeMove as apiMakeMove } from '../../utils/api';
import { getUserId } from '../../utils/userStorage';
import { GameBoard } from './GameBoard';
import { GameStatus } from './GameStatus';
import { PlayerInfo } from './PlayerInfo';
import { GameState, Move, PlayerId } from './types';

// Utility to create an empty 3x3 board
const emptyBoard = (): (PlayerId | null)[][] => Array.from({ length: 3 }, () => Array(3).fill(null));

// Pure function to apply a move to a board
function applyMove(state: GameState, move: Move): GameState {
  if (state.board[move.row][move.col] !== null) return state;
  const newBoard = state.board.map((row, r) =>
    row.map((cell, c) => (r === move.row && c === move.col ? move.player : cell))
  );
  const winner = checkWinner(newBoard, move.player);
  const draw = !winner && newBoard.flat().every((cell) => cell !== null);
  return {
    ...state,
    board: newBoard,
    winner: winner ? move.player : null,
    draw,
    currentTurn:
      (() => {
        const other = state.players.find((p: any) => (typeof p === 'string' ? p !== move.player : p.id !== move.player));
        if (typeof other === 'string' || typeof other === 'number') return other;
        if (typeof other === 'object') return other?.id || state.currentTurn;
        return state.currentTurn;
      })(),
  };
}

// Winner detection
function checkWinner(board: (PlayerId | null)[][], player: PlayerId): boolean {
  for (let i = 0; i < 3; i++) {
    if (board[i].every((cell) => cell === player)) return true;
    if (board.every((row) => row[i] === player)) return true;
  }
  if ([0, 1, 2].every((i) => board[i][i] === player)) return true;
  if ([0, 1, 2].every((i) => board[i][2 - i] === player)) return true;
  return false;
}

// Initial state for demo (replace with server state)
const initialState: GameState = {
  board: emptyBoard(),
  currentTurn: '1',
  players: [],
  winner: null,
  draw: false,
};

interface TicTacToeProps {
  sessionId?: string;
}

export const TicTacToe: React.FC<TicTacToeProps> = ({ sessionId }) => {
  // In real app, state comes from server and is updated via props or context
  const [gameState, setGameState] = useState<GameState>(initialState);

  // This handler would call the server in a real app
  const handleCellClick = async (row: number, col: number) => {
    if (gameState.winner || gameState.draw) return;
    // Only allow current player to move (simulate as player 1 for demo)
    // If we are connected to server session, call remote move
    if (sessionId) {
      const playerId = getUserId();
      if (!playerId) {
        alert('No user id set. Please set your name before playing');
        return;
      }
      try {
        await apiMakeMove(sessionId, playerId, row, col);
      } catch (e: any) {
        alert(e?.message || 'Move failed');
      }
      return;
    }

    const move: Move = { row, col, player: gameState.currentTurn };
    setGameState((prev) => applyMove(prev, move));
  };

  // When connected to a session, subscribe to state updates
  useEffect(() => {
    if (!sessionId) return;
    (async () => {
      const session = await apiGetSession(sessionId);
      if (session) {
        const remoteState: GameState = {
          board: session.board as any,
          currentTurn: session.currentTurn ?? session.players[0].id,
          players: session.players.map((p: any) => ({ id: p.id, name: p.name, icon: p.icon })),
          winner: session.winner ?? null,
          draw: !!session.draw,
        };
        setGameState(remoteState);
      }
    })();
    // initial state pushed above from apiGetSession
    const unsub = pollSession(sessionId, (s) => {
      if (!s) return;
      const remoteState: GameState = {
        board: s.board as any,
        currentTurn: s.currentTurn ?? s.players[0].id,
        players: s.players.map((p: any) => ({ id: p.id, name: p.name, icon: p.icon })),
        winner: s.winner ?? null,
        draw: !!s.draw,
      };
      setGameState(remoteState);
    });
    return () => unsub();
  }, [sessionId]);

  return (
    <div className="ttt-container">
      <PlayerInfo players={gameState.players as any} currentTurn={gameState.currentTurn} />
      <GameStatus currentTurn={gameState.currentTurn} winner={gameState.winner} draw={gameState.draw} players={gameState.players as any} />
      <GameBoard 
        board={gameState.board} 
        onCellClick={handleCellClick} 
        disabled={!!gameState.winner || gameState.draw}
        players={gameState.players as any}
      />
    </div>
  );
};
