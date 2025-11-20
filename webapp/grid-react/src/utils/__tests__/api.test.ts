/**
 * Integration tests for API client functions.
 * These tests verify that the API client correctly calls endpoints and handles responses.
 */

import {
  createUser,
  createSession,
  getSession,
  joinSession,
  makeMove,
  listSessions,
  pollSession,
  type Session,
  type SessionListItem,
} from '../api';

// Mock fetch globally
global.fetch = jest.fn();

const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

describe('API Client Integration Tests', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    // Set default API base
    process.env.NEXT_PUBLIC_API_BASE_URL = '/api';
  });

  describe('createUser', () => {
    it('should create a user with name and icon', async () => {
      const mockResponse = {
        id: 'user-123',
        name: 'Alice',
        icon: '😀',
        createdAt: '2024-01-01T00:00:00Z',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await createUser('Alice', '😀');

      expect(mockFetch).toHaveBeenCalledWith('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: 'Alice', icon: '😀' }),
      });

      expect(result).toEqual(mockResponse);
    });

    it('should create a user without icon', async () => {
      const mockResponse = {
        id: 'user-123',
        name: 'Bob',
        icon: null,
        createdAt: '2024-01-01T00:00:00Z',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await createUser('Bob');

      expect(mockFetch).toHaveBeenCalledWith('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: 'Bob' }),
      });

      expect(result).toEqual(mockResponse);
    });

    it('should handle API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({ message: 'Invalid name' }),
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      await expect(createUser('')).rejects.toThrow('Invalid name');
    });
  });

  describe('createSession', () => {
    it('should create a session', async () => {
      const mockResponse: Session = {
        id: 'session-123',
        players: [{ id: 'user-123', name: 'Alice', icon: '😀' }],
        status: 'WAITING',
        currentTurn: null,
        board: [[null, null, null], [null, null, null], [null, null, null]],
        moves: [],
        winner: null,
        draw: false,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await createSession({
        hostId: 'user-123',
        hostName: 'Alice',
        gameIcon: '🎮',
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hostId: 'user-123',
          hostName: 'Alice',
          gameIcon: '🎮',
        }),
      });

      expect(result).toEqual(mockResponse);
    });
  });

  describe('getSession', () => {
    it('should get a session by ID', async () => {
      const mockResponse: Session = {
        id: 'session-123',
        players: [
          { id: 'user-123', name: 'Alice', icon: '😀' },
          { id: 'user-456', name: 'Bob', icon: '🎯' },
        ],
        status: 'ACTIVE',
        currentTurn: 'user-123',
        board: [['user-123', null, null], [null, null, null], [null, null, null]],
        moves: [{ playerId: 'user-123', row: 0, col: 0 }],
        winner: null,
        draw: false,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await getSession('session-123');

      expect(mockFetch).toHaveBeenCalledWith('/api/sessions/session-123');
      expect(result).toEqual(mockResponse);
    });

    it('should handle 404 errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({ message: 'Session not found' }),
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      await expect(getSession('non-existent')).rejects.toThrow('Session not found');
    });
  });

  describe('joinSession', () => {
    it('should join a session', async () => {
      const mockResponse: Session = {
        id: 'session-123',
        players: [
          { id: 'user-123', name: 'Alice', icon: '😀' },
          { id: 'user-456', name: 'Bob', icon: '🎯' },
        ],
        status: 'ACTIVE',
        currentTurn: 'user-123',
        board: [[null, null, null], [null, null, null], [null, null, null]],
        moves: [],
        winner: null,
        draw: false,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await joinSession('session-123', 'user-456');

      expect(mockFetch).toHaveBeenCalledWith('/api/sessions/session-123/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playerId: 'user-456' }),
      });

      expect(result).toEqual(mockResponse);
    });
  });

  describe('makeMove', () => {
    it('should make a move', async () => {
      const mockResponse: Session = {
        id: 'session-123',
        players: [
          { id: 'user-123', name: 'Alice', icon: '😀' },
          { id: 'user-456', name: 'Bob', icon: '🎯' },
        ],
        status: 'ACTIVE',
        currentTurn: 'user-456',
        board: [['user-123', null, null], [null, null, null], [null, null, null]],
        moves: [{ playerId: 'user-123', row: 0, col: 0 }],
        winner: null,
        draw: false,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await makeMove('session-123', 'user-123', 0, 0);

      expect(mockFetch).toHaveBeenCalledWith('/api/sessions/session-123/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playerId: 'user-123', row: 0, col: 0 }),
      });

      expect(result).toEqual(mockResponse);
    });

    it('should handle move conflicts', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 409,
        statusText: 'Conflict',
        json: async () => ({ message: 'It is not your turn' }),
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      await expect(makeMove('session-123', 'user-123', 0, 0)).rejects.toThrow(
        'It is not your turn'
      );
    });
  });

  describe('listSessions', () => {
    it('should list sessions without filters', async () => {
      const mockResponse = {
        items: [
          {
            id: 'session-123',
            host: { id: 'user-123', name: 'Alice', icon: '😀' },
            gameIcon: '🎮',
            status: 'WAITING',
            players: [{ id: 'user-123', name: 'Alice', icon: '😀' }],
            createdAt: '2024-01-01T00:00:00Z',
          } as SessionListItem,
        ],
        nextCursor: null,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await listSessions();

      expect(mockFetch).toHaveBeenCalledWith('/api/sessions');
      expect(result).toEqual(mockResponse);
    });

    it('should list sessions with filters', async () => {
      const mockResponse = {
        items: [] as SessionListItem[],
        nextCursor: null,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await listSessions({
        status: 'ACTIVE',
        hostId: 'user-123',
        limit: 10,
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/sessions?status=ACTIVE&hostId=user-123&limit=10');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('pollSession', () => {
    it('should poll session and call callback', async () => {
      jest.useFakeTimers();

      const mockSession: Session = {
        id: 'session-123',
        players: [{ id: 'user-123', name: 'Alice', icon: '😀' }],
        status: 'ACTIVE',
        currentTurn: 'user-123',
        board: [[null, null, null], [null, null, null], [null, null, null]],
        moves: [],
        winner: null,
        draw: false,
      };

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockSession,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const callback = jest.fn();
      const cancel = pollSession('session-123', callback, 1000);

      // Fast-forward time to trigger polling
      jest.advanceTimersByTime(1000);
      await Promise.resolve(); // Wait for async operations

      expect(callback).toHaveBeenCalledWith(mockSession);

      cancel();
      jest.useRealTimers();
    });
  });
});

