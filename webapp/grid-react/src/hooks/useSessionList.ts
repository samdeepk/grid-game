import { useState, useEffect, useCallback } from 'react';
import { listSessions, SessionListItem } from '../utils/api';

interface UseSessionListResult {
  sessions: SessionListItem[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export const useSessionList = (userId: string | null): UseSessionListResult => {
  const [sessions, setSessions] = useState<SessionListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    if (!userId) {
      setSessions([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await listSessions({ hostId: userId, limit: 50 });
      // Filter logic moved here
      const userSessions = response.items.filter(
        (session) =>
          session.host.id === userId ||
          session.players.some((player) => player.id === userId)
      );
      setSessions(userSessions);
    } catch (err: any) {
      setError(err.message || 'Failed to load games');
      setSessions([]);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return { sessions, loading, error, refresh: fetchSessions };
};

