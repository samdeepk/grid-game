import React, { useMemo, useEffect, useRef } from 'react';
import { useGameSession } from '../../hooks/useGameSession';
import { useTicTacToe } from '../../hooks/useTicTacToe';
import { GameBoard } from './GameBoard';
import { GameStatus } from './GameStatus';
import { PlayerInfo } from './PlayerInfo';
import { useUser } from '../../context/UserContext';
import { useToast } from '../../context/ToastContext';
import party from 'party-js';
import { createSession } from '../../utils/api';
import './tic-tac-toe.scss';

interface TicTacToeProps {
  sessionId?: string;
}

export const TicTacToe: React.FC<TicTacToeProps> = ({ sessionId }) => {
  const { session, loading, error: sessionError } = useGameSession(sessionId);
  const { makeMove, isSubmitting, error: moveError } = useTicTacToe(session);
  const { user } = useUser();
  const { showToast } = useToast();
  const prevWinnerRef = useRef<string | number | null | undefined>(undefined);

  // Show move errors as toasts
  useEffect(() => {
    if (moveError) {
      showToast(moveError, 'error');
    }
  }, [moveError, showToast]);

  // Handle Party.js effects on win
  useEffect(() => {
    const currentWinner = session?.winner;
    if (currentWinner && prevWinnerRef.current === null) {
      party.confetti(document.body, {
        count: party.variation.range(60, 100),
        size: party.variation.range(0.8, 1.4),
      });
    }
    prevWinnerRef.current = currentWinner;
  }, [session?.winner]);

  const handleCellClick = async (row: number, col: number) => {
    if (!session || !user) return;
    await makeMove(row, col);
  };

  const handleHome = () => {
    window.location.href = '/';
  };

  const handlePlayAgain = async () => {
    if (!user) return;
    try {
        const newSession = await createSession({
            hostId: user.id,
            hostName: user.name,
            hostIcon: user.icon,
            gameIcon: session?.gameIcon || undefined
        });
        // Redirect to the new session
        window.location.href = `/game/${newSession.id}`;
    } catch (err) {
        showToast('Failed to create new game', 'error');
    }
  };

  // Computed properties for UI state
  const isMyTurn = useMemo(() => {
    return session?.status === 'ACTIVE' && session?.currentTurn === user?.id;
  }, [session, user]);

  const isDisabled = useMemo(() => {
    return (
      !session ||
      session.status !== 'ACTIVE' ||
      !isMyTurn ||
      isSubmitting ||
      !!session.winner ||
      !!session.draw
    );
  }, [session, isMyTurn, isSubmitting]);

  if (loading) {
    return <div className="ttt-loading">Loading game...</div>;
  }

  if (sessionError) {
    return <div className="ttt-error">Error: {sessionError}</div>;
  }

  if (!sessionId || !session) {
    return <div className="ttt-empty">No active session</div>;
  }

  const isGameOver = !!session.winner || session.draw;

  return (
    <div className="ttt-container">
      <div className="ttt-status-container">
        <GameStatus 
            currentTurn={session.currentTurn || null} 
            winner={session.winner || null} 
            draw={session.draw} 
            players={session.players} 
        />
      </div>

      <div className="ttt-players">
        <PlayerInfo 
            players={session.players} 
            currentTurn={session.currentTurn || null} 
        />
      </div>

      <GameBoard 
        board={session.board} 
        onCellClick={handleCellClick} 
        disabled={isDisabled} 
        players={session.players}
      />

      {isGameOver && (
        <div className="ttt-controls">
          <button className="btn-control secondary" onClick={handleHome}>
            Home
          </button>
          <button className="btn-control primary" onClick={handlePlayAgain}>
            Play New Game
          </button>
        </div>
      )}
    </div>
  );
};
