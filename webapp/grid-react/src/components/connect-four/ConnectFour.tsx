import React, { useEffect, useState } from 'react';
import { getSession as apiGetSession, pollSession, makeMove as apiMakeMove } from '../../utils/api';
import { getUserId } from '../../utils/userStorage';
import { ConnectFourBoard } from './ConnectFourBoard';
import { GameStatus } from '../tic-tac-toe/GameStatus';
import { PlayerInfo } from '../tic-tac-toe/PlayerInfo';
import { GameState, Move,  } from './types';
import {  PlayerId } from '../../types/game';


import './connect-four.scss';

// Utility to create an empty 6x7 board
const emptyBoard = (): (PlayerId | null)[][] => 
  Array.from({ length: 6 }, () => Array(7).fill(null));

// Find the lowest empty row in a column
function findDropRow(board: (PlayerId | null)[][], col: number): number | null {
  for (let row = board.length - 1; row >= 0; row--) {
    if (board[row][col] === null) {
      return row;
    }
  }
  return null;
}

// Pure function to apply a move to a board
function applyMove(state: GameState, move: Move): GameState {
  const dropRow = findDropRow(state.board, move.col);
  if (dropRow === null) return state; // Column is full
  
  if (state.board[dropRow][move.col] !== null) return state; // Already occupied
  
  const newBoard = state.board.map((row, r) =>
    row.map((cell, c) => (r === dropRow && c === move.col ? move.player : cell))
  );
  
  const winner = checkWinner(newBoard, dropRow, move.col, move.player);
  const draw = !winner && newBoard.flat().every((cell) => cell !== null);
  
  return {
    ...state,
    board: newBoard,
    winner: winner ? move.player : null,
    draw,
    currentTurn: state.players.find((p) => p.id !== move.player)?.id ?? state.currentTurn,
  };
}

// Winner detection - check for 4 in a row
function checkWinner(
  board: (PlayerId | null)[][], 
  row: number, 
  col: number, 
  player: PlayerId
): boolean {
  const directions = [
    [0, 1],   // horizontal
    [1, 0],   // vertical
    [1, 1],   // diagonal down-right
    [1, -1],  // diagonal down-left
  ];

  for (const [dr, dc] of directions) {
    let count = 1; // Count the current piece

    // Check in positive direction
    for (let i = 1; i < 4; i++) {
      const r = row + dr * i;
      const c = col + dc * i;
      if (r >= 0 && r < board.length && c >= 0 && c < board[0].length && board[r][c] === player) {
        count++;
      } else {
        break;
      }
    }

    // Check in negative direction
    for (let i = 1; i < 4; i++) {
      const r = row - dr * i;
      const c = col - dc * i;
      if (r >= 0 && r < board.length && c >= 0 && c < board[0].length && board[r][c] === player) {
        count++;
      } else {
        break;
      }
    }

    if (count >= 4) {
      return true;
    }
  }

  return false;
}

// Initial state
const initialState: GameState = {
  board: emptyBoard(),
  currentTurn: '1',
  players: [],
  winner: null,
  draw: false,
};

interface ConnectFourProps {
  sessionId?: string;
}

export const ConnectFour: React.FC<ConnectFourProps> = ({ sessionId }) => {
  const [gameState, setGameState] = useState<GameState>(initialState);

  // Handle column click - drop piece in that column
  const handleColumnClick = async (col: number) => {
    if (gameState.winner || gameState.draw) return;
    
    if (sessionId) {
      const playerId = getUserId();
      if (!playerId) {
        alert('No user id set. Please set your name before playing');
        return;
      }
      
      // Find the drop row for this column
      const dropRow = findDropRow(gameState.board, col);
      if (dropRow === null) {
        alert('This column is full');
        return;
      }
      
      try {
        await apiMakeMove(sessionId, playerId, dropRow, col);
      } catch (e: any) {
        alert(e?.message || 'Move failed');
      }
      return;
    }

    // Local play (for testing)
    const dropRow = findDropRow(gameState.board, col);
    if (dropRow === null) return;
    
    const move: Move = { row: dropRow, col, player: gameState.currentTurn };
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
    
    // Poll for updates
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
    <div className="c4-container">
      <PlayerInfo players={gameState.players} currentTurn={gameState.currentTurn} />
      <GameStatus 
        currentTurn={gameState.currentTurn} 
        winner={gameState.winner} 
        draw={gameState.draw} 
        players={gameState.players} 
      />
      <ConnectFourBoard 
        board={gameState.board} 
        onColumnClick={handleColumnClick} 
        disabled={!!gameState.winner || gameState.draw}
        players={gameState.players}
      />
    </div>
  );
};

