# Grid Game Backend API Contract

This document specifies the REST API endpoints and contracts for the grid-based game (3x3 Tic-Tac-Toe style). Use this as the authoritative reference while implementing the backend.

Base URL (example)
- Production: `https://api.example.com`
- Local dev: `http://localhost:8000`
- In the frontend we use `NEXT_PUBLIC_API_BASE_URL` to override default `/api`.

Auth
- For the take-home, a simple user id sent in request bodies is sufficient.
- In production, protect endpoints with authentication (JWT/session).

---

## Resources and Endpoints

1) Create user
- Method: POST
- Path: `/users`
- Description: Create or register a player. Returns a stable `userId` used for game actions.
- Request JSON:
  {
    "name": "string",
    "icon": "string (optional, emoji or url)"
  }
- Response 201:
  {
    "id": "string",
    "name": "string",
    "icon": "string | null",
    "createdAt": "ISO8601"
  }
- Errors: 400 (validation)

2) Create session
- Method: POST
- Path: `/sessions`
- Description: Create a new game session. Caller becomes the host and the first player. The host picks an emoji/icon to identify this session in the lobby.
- Request JSON:
  {
    "hostId": "string",
    "hostName": "string",
    "hostIcon": "string (optional)",
    "gameIcon": "string (optional, emoji shown in lobby card)"
  }
- Response 201:
  {
    "id": "string",
    "players": [ { "id": "string", "name": "string", "icon": "string" } ],
    "status": "WAITING",
    "currentTurn": null,
    "board": [[null,null,null],[null,null,null],[null,null,null]],
    "moves": [],
    "gameIcon": "string | null",
    "createdAt": "ISO8601"
  }
- Errors: 400 (validation)

3) List sessions
- Method: GET
- Path: `/sessions`
- Description: Return paginated sessions for the lobby. Default filters to sessions created in the last N hours (configurable) ordered by `createdAt DESC`.
- Query params:
  - `status` (optional, WAITING|ACTIVE|FINISHED) – filter by status
  - `hostId` (optional) – sessions created by a host
  - `limit` (default 20, max 100)
  - `cursor` or `page` (optional) – paging token/number
- Response 200:
  {
    "items": [
      {
        "id": "string",
        "host": { "id": "string", "name": "string", "icon": "string | null" },
        "gameIcon": "string | null",
        "status": "WAITING" | "ACTIVE" | "FINISHED",
        "players": [{ "id": "string", "name": "string", "icon": "string | null" }],
        "createdAt": "ISO8601"
      }
    ],
    "nextCursor": "string | null"
  }
- Errors: 400 (bad paging params)

4) Get session
- Method: GET
- Path: `/sessions/{sessionId}`
- Description: Return full session state (board, players, status, moves, winner/draw)
- Response 200:
  {
    "id": "string",
    "players": [ { "id": "string", "name": "string", "icon": "string" } ],
    "status": "WAITING" | "ACTIVE" | "FINISHED",
    "currentTurn": "string | null",
    "board": [["string|null"]],
    "moves": [{ "playerId": "string", "row": 0-2, "col": 0-2, "moveNo": number }],
    "winner": "string | null",
    "draw": boolean,
    "createdAt": "ISO8601"
  }
- Errors: 404 if not found

5) Join session
- Method: POST
- Path: `/sessions/{sessionId}/join`
- Description: Add a player to a waiting session. When the second player joins, session becomes `ACTIVE` and `currentTurn` is set.
- Request JSON:
  {
    "playerId": "string"
  }
- Response 200:
  - Returns updated Session object (see Get session response)
- Errors: 400 if invalid (session finished, already full), 404 if session not found.

6) Submit move
- Method: POST
- Path: `/sessions/{sessionId}/move`
- Description: Submit a move. The server validates turn order and cell occupancy, updates game state, checks for win/draw, and returns updated session.
- Request JSON:
  {
    "playerId": "string",
    "row": 0-2,
    "col": 0-2
  }
- Success Response 200:
  - Updated session object (see Get session response)
- Error Responses:
  - 400 Bad Request — invalid coordinates, missing fields
  - 409 Conflict — move invalid (cell already occupied, not player's turn)
  - 404 Not Found — session not found

7) Leaderboard (optional)
- Method: GET
- Path: `/leaderboard?metric=win_count|efficiency&limit=3`
- Description: Return top players ordered by `win_count` (desc) or `efficiency` (average moves per win; lower is better)
- Response 200:
  [
    { "playerId": "string", "name": "string", "wins": number, "efficiency": number | null },
    ...
  ]

---

## Data Model Notes
- Session
  - id: string (UUID)
  - players: array[1..2] of player objects { id, name, icon }
  - status: WAITING | ACTIVE | FINISHED
  - currentTurn: playerId or null
  - board: 3x3 matrix of playerId | null
  - moves: ordered append-only list (playerId, row, col, moveNo, createdAt)
  - winner: playerId | null
  - draw: boolean

- Player
  - id: string (UUID)
  - name: string
  - icon: string | null
  - stats stored separately (wins, losses, draws, totalMovesForWins)

## Concurrency & Validation Guidance
- Validate move under transaction/lock to avoid race conditions:
  - Option A (Relational DB): SELECT session row FOR UPDATE; re-check cell empty & currentTurn; append move; update state; commit.
  - Option B (Optimistic): write move to moves table with unique(session,row,col); recompute state and update session using CAS on session.version.
- Only accept moves when `session.status === 'ACTIVE'` and `playerId === session.currentTurn`.
- Moves must be within 0-2 coordinates and target cell must be empty.

## Winner detection algorithm
- After inserting a move for (r,c) by player P, check counts:
  - Row r: count moves by P in row r
  - Column c: count moves by P in column c
  - Main diagonal if r===c
  - Anti-diagonal if r+c===2
- If any count reaches 3, set session.status = FINISHED and winner = P
- If move count reaches 9 and no winner, set draw=true and session.status=FINISHED

## WebSocket Option (recommended for real-time UX)
- WS path: `/ws/sessions/{sessionId}`
- Server broadcasts session object on every change.
- Fallback: Polling `GET /sessions/{id}` (used in current frontend polling client)

## Error codes & payload
- 400: { message: string, details?: any }
- 404: { message: 'Not found' }
- 409: { message: 'Conflict - reason' }
- 500: { message: 'Internal server error' }

## Example Move Request/Response
Request:
POST /sessions/abcd1234/move
{
  "playerId": "user-1",
  "row": 0,
  "col": 1
}

Success (200):
{
  "id": "abcd1234",
  "players": [{"id":"user-1","name":"Alice"},{"id":"user-2","name":"Bob"}],
  "status": "ACTIVE",
  "currentTurn": "user-2",
  "board": [[null,"user-1",null],[null,null,null],[null,null,null]],
  "moves": [{"playerId":"user-1","row":0,"col":1,"moveNo":1}],
  "winner": null,
  "draw": false
}

## Admin / Ops notes
- Persist sessions and moves for audit and to compute leaderboard.
- Use background job to compute leaderboard from completed sessions, or compute on the fly using aggregated queries.
- Keep `moves` as append-only audit trail.

---

If you'd like, I can now:
- Implement a minimal Express/FastAPI server that matches this contract (endpoints + in-memory store) so you can test cross-tab play without polling changes, or
- Replace the current frontend polling with WebSocket client code (subscribe to `/ws/sessions/:id`) using this contract.

Which would you prefer next?