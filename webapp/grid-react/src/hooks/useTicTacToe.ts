import { useCallback, useState } from 'react';
import { makeMove as apiMakeMove } from '../utils/api';
import { useUser } from '../context/UserContext';
import { GameSession } from '../types/game';

interface UseTicTacToeResult {
  makeMove: (row: number, col: number) => Promise<void>;
  isSubmitting: boolean;
  error: string | null;
}

export const useTicTacToe = (
  session: GameSession | null, 
  onMoveSuccess?: () => void
): UseTicTacToeResult => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useUser();

  const makeMove = useCallback(async (row: number, col: number) => {
    if (!session) return;
    
    if (session.status !== 'ACTIVE') {
        return;
    }

    if (!user?.id) {
      setError('User not identified. Please set your name.');
      return;
    }

    if (session.currentTurn !== user.id) {
        return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await apiMakeMove(session.id, user.id, row, col);
      if (onMoveSuccess) onMoveSuccess();
    } catch (err: any) {
      setError(err.message || 'Failed to make move');
    } finally {
      setIsSubmitting(false);
    }
  }, [session, user, onMoveSuccess]);

  return { makeMove, isSubmitting, error };
};
