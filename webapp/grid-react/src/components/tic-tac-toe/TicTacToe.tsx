import React, { useMemo, useEffect } from 'react';
import { useGameSession } from '../../hooks/useGameSession';
import { useTicTacToe } from '../../hooks/useTicTacToe';
import { GameBoard } from './GameBoard';
import { GameStatus } from './GameStatus';
import { PlayerInfo } from './PlayerInfo';
import { useUser } from '../../context/UserContext';
import { useToast } from '../../context/ToastContext';

interface TicTacToeProps {
  sessionId?: string;
}

export const TicTacToe: React.FC<TicTacToeProps> = ({ sessionId }) => {
  const { session, loading, error: sessionError } = useGameSession(sessionId);
  const { makeMove, isSubmitting, error: moveError } = useTicTacToe(session);
  const { user } = useUser();
  const { showToast } = useToast();

  // Show move errors as toasts
  useEffect(() => {
    if (moveError) {
      showToast(moveError, 'error');
    }
  }, [moveError, showToast]);

  const handleCellClick = async (row: number, col: number) => {
    if (!session || !user) return;
    await makeMove(row, col);
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

  return (
    <div className="ttt-container">
      <PlayerInfo 
        players={session.players} 
        currentTurn={session.currentTurn || null} 
      />
      
      <GameStatus 
        currentTurn={session.currentTurn || null} 
        winner={session.winner || null} 
        draw={session.draw} 
        players={session.players} 
      />
      
      <GameBoard 
        board={session.board} 
        onCellClick={handleCellClick} 
        disabled={isDisabled} 
      />
    </div>
  );
};
