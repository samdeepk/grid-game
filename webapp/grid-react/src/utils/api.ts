// Simple REST client to interact with the backend API for game sessions

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '/api').replace(/\/$/, '');

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
};

export async function createUser(name: string, icon?: string) {
  return await jsonFetch('/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, icon }),
  });
}

export async function createSession(hostId: string) {
  return await jsonFetch('/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hostId }),
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

// Poll for changes every `intervalMs`. Returns a function to cancel
export function pollSession(sessionId: string, cb: (s: Session | null) => void, intervalMs = 1200) {
  let cancelled = false;
  async function tick() {
    try {
      const s = await getSession(sessionId);
      if (!cancelled) cb(s);
    } catch (e) {
      if (!cancelled) cb(null);
    }
    if (cancelled) return;
    setTimeout(() => tick(), intervalMs);
  }
  tick();
  return () => {
    cancelled = true;
  };
}
