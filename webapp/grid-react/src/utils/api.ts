// Simple REST client to interact with the backend API for game sessions

const rawBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
const API_BASE = rawBase.replace(/\/$/, '');

async function jsonFetch(path: string, opts: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${path}`, opts);
  const isJson = res.headers.get('content-type')?.includes('application/json');
  const data = isJson ? await res.json() : null;
  if (!res.ok) {
    throw new Error(data?.message || res.statusText || 'API error');
  }
  return data;
}

export type Player = { id: string; name: string; icon?: string };
export type Session = {
  id: string;
  players: Player[];
  status: 'WAITING' | 'ACTIVE' | 'FINISHED';
  currentTurn?: string | null;
  board: (string | null)[][];
  moves: { playerId: string; row: number; col: number }[];
  winner?: string | null;
  draw?: boolean;
  gameType?: string;
};

export type SessionListItem = {
  id: string;
  host: { id: string; name: string; icon: string | null };
  gameIcon: string | null;
  status: 'WAITING' | 'ACTIVE' | 'FINISHED';
  players: Player[];
  createdAt: string;
};

export type SessionsListResponse = {
  items: SessionListItem[];
  nextCursor: string | null;
};

export type PollSessionOptions = {
  intervalMs?: number;
  maxDurationMs?: number;
  stopWhen?: (session: Session | null) => boolean;
};

export async function createUser(name: string, icon?: string) {
  return await jsonFetch('/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, icon }),
  });
}

type CreateSessionPayload = {
  hostId: string;
  hostName?: string;
  hostIcon?: string | null;
  gameIcon?: string | null;
  gameType?: string;
};

export async function createSession(payload: CreateSessionPayload) {
  return await jsonFetch('/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }) as Session;
}

export async function getSession(sessionId: string) {
  return await jsonFetch(`/sessions/${sessionId}`) as Session;
}

export async function joinSession(sessionId: string, playerId: string) {
  return await jsonFetch(`/sessions/${sessionId}/join`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ playerId }),
  }) as Session;
}

export async function makeMove(sessionId: string, playerId: string, row: number, col: number) {
  return await jsonFetch(`/sessions/${sessionId}/move`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ playerId, row, col }),
  }) as Session;
}

export async function listSessions(params?: {
  status?: 'WAITING' | 'ACTIVE' | 'FINISHED';
  hostId?: string;
  limit?: number;
  cursor?: string;
}): Promise<SessionsListResponse> {
  const queryParams = new URLSearchParams();
  if (params?.status) queryParams.append('status', params.status);
  if (params?.hostId) queryParams.append('hostId', params.hostId);
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.cursor) queryParams.append('cursor', params.cursor);

  const queryString = queryParams.toString();
  const path = `/sessions${queryString ? `?${queryString}` : ''}`;
  return await jsonFetch(path) as SessionsListResponse;
}

// Poll for changes. Returns a function to cancel
export function pollSession(
  sessionId: string,
  cb: (s: Session | null) => void,
  options: number | PollSessionOptions = {},
) {
  const resolvedOptions: PollSessionOptions =
    typeof options === 'number' ? { intervalMs: options } : options;

  const intervalMs = resolvedOptions.intervalMs ?? 1200;
  const maxDurationMs = resolvedOptions.maxDurationMs;
  const stopWhen = resolvedOptions.stopWhen;

  let cancelled = false;
  const startedAt = Date.now();

  const shouldStopForDuration = () =>
    typeof maxDurationMs === 'number' && maxDurationMs > 0 && Date.now() - startedAt >= maxDurationMs;

  async function tick() {
    if (cancelled || shouldStopForDuration()) {
      cancelled = true;
      return;
    }

    let session: Session | null = null;
    try {
      session = await getSession(sessionId);
      if (!cancelled) cb(session);
    } catch (e) {
      if (!cancelled) cb(null);
    }

    if (cancelled) return;
    if (stopWhen && stopWhen(session)) {
      cancelled = true;
      return;
    }
    if (shouldStopForDuration()) {
      cancelled = true;
      return;
    }

    setTimeout(() => tick(), intervalMs);
  }

  tick();
  return () => {
    cancelled = true;
  };
}
