import { useState, useEffect, useCallback } from 'react';
import { getSession, pollSession, Session } from '../utils/api';
import { GameSession } from '../types/game';

interface UseGameSessionResult {
  session: GameSession | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export const useGameSession = (sessionId?: string): UseGameSessionResult => {
  const [session, setSession] = useState<GameSession | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSession = useCallback(async () => {
    if (!sessionId) return;
    try {
      const data = await getSession(sessionId);
      // Transform API Session to our GameSession type if needed, 
      // currently they are compatible but it's good to have a mapping layer if they diverge.
      setSession(data as unknown as GameSession);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch session');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    if (!sessionId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    fetchSession();

    const unsub = pollSession(sessionId, (data: Session | null) => {
      if (data) {
        setSession(data as unknown as GameSession);
        setError(null);
      }
    });

    return () => {
      unsub();
    };
  }, [sessionId, fetchSession]);

  return { session, loading, error, refresh: fetchSession };
};

