# Grid Game - Code Walkthrough Documentation
## Backend Engineer (70%) + Frontend Engineer (30%) Interview

---

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Backend Architecture (70%)](#backend-architecture-70)
4. [Frontend Architecture (30%)](#frontend-architecture-30)
5. [Key Flows & Use Cases](#key-flows--use-cases)
6. [Database Schema](#database-schema)
7. [API Design](#api-design)
8. [Design Decisions & Trade-offs](#design-decisions--trade-offs)

---

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────┐         HTTP/REST          ┌─────────────────┐
│                 │ ◄─────────────────────────► │                 │
│   Next.js       │      (JSON over HTTP)       │   FastAPI       │
│   Frontend      │                             │   Backend       │
│   (React/TS)    │                             │   (Python)      │
│                 │                             │                 │
└─────────────────┘                             └────────┬────────┘
                                                          │
                                                          │ SQLAlchemy ORM
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │   PostgreSQL    │
                                                 │   Database      │
                                                 │   (Supabase)    │
                                                 └─────────────────┘
```

### Core Components

1. **Frontend (Next.js/React)**: Client-side UI, state management, polling
2. **Backend (FastAPI)**: REST API, game logic, database operations
3. **Database (PostgreSQL)**: Persistent storage for users, sessions, moves

---

## Technology Stack

### Backend (70% Focus)
- **Framework**: FastAPI (async Python web framework)
- **ORM**: SQLAlchemy (async)
- **Database**: PostgreSQL (via Supabase)
- **Migrations**: Alembic
- **Architecture**: RESTful API, extensible game logic system

### Frontend (30% Focus)
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **UI Library**: React
- **Styling**: SCSS
- **State Management**: React hooks (useState, useEffect, useContext)
- **API Client**: Custom fetch wrapper with polling

---

## Backend Architecture (70%)

### 1. Project Structure

```
server/py3/
├── main.py              # FastAPI app, routes, request/response models
├── database.py          # DB connection, session management
├── game_logic.py        # Extensible game logic system
├── models/
│   ├── user.py          # User model
│   ├── session.py       # Session model (game state)
│   └── move.py          # Move model (audit trail)
├── alembic/             # Database migrations
└── requirements.txt     # Dependencies
```

### 2. Core Backend Components

#### 2.1 Database Models

**User Model** (`models/user.py`)
- Stores player information
- Fields: `id`, `name`, `icon`, `created_at`
- Simple identity model (no authentication)

**Session Model** (`models/session.py`)
- Represents a game session
- **Key Fields**:
  - `id`: Unique session identifier
  - `host_id`, `host_name`, `host_icon`: First player
  - `guest_id`, `guest_name`, `guest_icon`: Second player
  - `game_type`: Extensible field ('tic_tac_toe', 'connect_four')
  - `status`: 'WAITING' | 'ACTIVE' | 'FINISHED'
  - `board`: JSON string of board state
  - `current_turn`: Player ID whose turn it is
  - `winner`: Player ID who won (nullable)
  - `draw`: Boolean flag
- **Helper Methods**:
  - `get_board()`: Deserialize JSON to 2D array
  - `set_board()`: Serialize 2D array to JSON
  - `_get_default_board()`: Game-type specific default board

**Move Model** (`models/move.py`)
- Audit trail of all moves
- Fields: `id`, `session_id`, `player_id`, `row`, `col`, `move_no`, `created_at`
- Enables replay, history, debugging

#### 2.2 Game Logic System (`game_logic.py`)

**Design Pattern**: Strategy Pattern with Factory

```python
GameLogic (Abstract Base Class)
├── TicTacToeLogic
└── ConnectFourLogic
```

**Key Methods**:
- `get_default_board()`: Returns empty board for game type
- `validate_move()`: Checks if move is legal
- `check_winner()`: Determines if move results in win
- `check_draw()`: Determines if game is a draw
- `get_board_size()`: Returns (rows, cols) tuple

**Extensibility**: New games can be added by:
1. Creating new `GameLogic` subclass
2. Registering in `get_game_logic()` factory function

#### 2.3 API Endpoints (`main.py`)

**User Management**:
- `POST /users`: Create user (returns user ID)

**Session Management**:
- `POST /sessions`: Create new game session
- `GET /sessions/{sessionId}`: Get full session state
- `GET /sessions`: List sessions (with filtering, pagination)
- `POST /sessions/{sessionId}/join`: Join waiting session
- `POST /sessions/{sessionId}/move`: Make a move

**Request/Response Models** (Pydantic):
- `CreateUserRequest`
- `CreateSessionRequest`
- `JoinSessionRequest`
- `MakeMoveRequest`

**Serialization Functions**:
- `serialize_session()`: Converts DB model to API response
- `serialize_session_list_item()`: Simplified version for list view

### 3. Backend Flow: Creating a Session

```
1. Client: POST /sessions
   {
     "hostId": "user-123",
     "hostName": "Alice",
     "gameType": "tic_tac_toe"
   }

2. Backend:
   a. Validate host user exists (DB query)
   b. Get game logic for game_type
   c. Create Session record:
      - Generate UUID
      - Set status = 'WAITING'
      - Initialize board (via game_logic.get_default_board())
      - Store board as JSON string
   d. Save to database
   e. Return serialized session

3. Response: 201 Created
   {
     "id": "session-abc",
     "status": "WAITING",
     "board": [[null, null, null], ...],
     "players": [{"id": "user-123", ...}],
     ...
   }
```

### 4. Backend Flow: Joining a Session

```
1. Client: POST /sessions/{sessionId}/join
   { "playerId": "user-456" }

2. Backend Validation:
   a. Load session with row lock (SELECT ... FOR UPDATE)
   b. Check session exists → 404 if not
   c. Check status == 'WAITING' → 400 if not
   d. Check user exists → 404 if not
   e. Check host != guest → 400 if same
   f. Check guest_id is null → 400 if full

3. Update Session:
   a. Set guest_id, guest_name, guest_icon
   b. Set status = 'ACTIVE'
   c. Set current_turn = host_id (host goes first)
   d. Commit transaction

4. Response: 200 OK (full session state)
```

### 5. Backend Flow: Making a Move

```
1. Client: POST /sessions/{sessionId}/move
   {
     "playerId": "user-123",
     "row": 1,
     "col": 1
   }

2. Backend Validation:
   a. Load session with row lock (race condition prevention)
   b. Check session.status == 'ACTIVE' → 400 if not
   c. Check current_turn == playerId → 400 if not user's turn
   d. Load board from JSON
   e. Get game logic for session.game_type
   f. Validate move (game_logic.validate_move())
      - Check coordinates valid
      - Check cell empty
      - Game-specific rules (e.g., Connect 4 drop position)

3. Apply Move:
   a. Update board: board[row][col] = playerId
   b. Check for winner (game_logic.check_winner())
   c. Check for draw (game_logic.check_draw())
   d. Update current_turn (switch to other player)
   e. Save board as JSON
   f. Create Move record (audit trail)
   g. Commit transaction

4. Response: 200 OK (updated session state)
```

### 6. Concurrency & Race Conditions

**Problem**: Multiple requests trying to join/move simultaneously

**Solution**: Row-level locking
```python
result = await db.execute(
    select(Session)
    .where(Session.id == session_id)
    .with_for_update()  # PostgreSQL row lock
)
```

**Why it works**:
- First transaction acquires lock
- Subsequent transactions wait
- Prevents double-join, invalid moves

### 7. Database Migrations (Alembic)

**Migration Strategy**:
- Version-controlled schema changes
- Files in `alembic/versions/`
- Examples:
  - `0001_add_guest_columns.py`: Added guest player fields
  - `0002_add_session_fields.py`: Added game state fields

**Migration Flow**:
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## Frontend Architecture (30%)

### 1. Project Structure

```
webapp/grid-react/
├── app/                          # Next.js App Router
│   ├── page.tsx                  # Home page
│   ├── game/[sessionId]/
│   │   └── GamePageClient.tsx    # Game page (client component)
│   ├── join/[gameId]/
│   │   └── JoinPageClient.tsx    # Join page
│   └── waiting/[sessionId]/
│       └── WaitingPageClient.tsx # Waiting room
├── src/
│   ├── components/
│   │   ├── tic-tac-toe/          # TicTacToe game component
│   │   ├── connect-four/         # ConnectFour game component
│   │   ├── game-list/            # Session list
│   │   ├── create-game-modal/    # Create game UI
│   │   └── waiting-room/         # Waiting room UI
│   ├── hooks/
│   │   ├── useGameSession.ts     # Session state management
│   │   └── useTicTacToe.ts       # Game-specific logic
│   ├── context/
│   │   ├── UserContext.tsx       # User state (localStorage)
│   │   └── ToastContext.tsx      # Toast notifications
│   └── utils/
│       ├── api.ts                # API client + polling
│       └── userStorage.ts        # localStorage helpers
└── next.config.js                 # API proxy configuration
```

### 2. Frontend State Management

**User State** (`context/UserContext.tsx`):
- Stored in localStorage (no backend auth)
- Keys: `grid-game-user-id`, `grid-game-user-name`, `grid-game-user-icon`
- Context provides: `user`, `login()`, `logout()`

**Session State** (`hooks/useGameSession.ts`):
- Fetches session on mount
- Polls for updates (with timeout & stop conditions)
- Returns: `session`, `loading`, `error`, `refresh()`

**Polling System** (`utils/api.ts`):
```typescript
pollSession(sessionId, callback, options)
```
- Options: `intervalMs`, `maxDurationMs`, `stopWhen`
- Automatically stops after timeout or when game ends
- Returns cancel function for cleanup

### 3. Frontend Flow: Creating & Joining a Game

```
1. User lands on home page (/)
   └─> Check localStorage for user
       ├─> No user → Show UserNameModal
       └─> Has user → Show game list + create button

2. User creates game:
   └─> Click "Create Game"
       └─> Show CreateGameModal
           └─> Select game icon/type
               └─> POST /api/sessions
                   └─> Redirect to /waiting/{sessionId}

3. Waiting Room (/waiting/{sessionId}):
   └─> useGameSession hook polls for updates
       └─> When status === 'ACTIVE'
           └─> Redirect to /game/{sessionId}

4. Second player joins:
   └─> Visit /join/{sessionId}
       └─> POST /api/sessions/{sessionId}/join
           └─> Redirect to /game/{sessionId}
```

### 4. Frontend Flow: Playing the Game

```
1. Game Page (/game/{sessionId}):
   └─> GamePageClient component
       ├─> Fetch session (GET /api/sessions/{sessionId})
       ├─> Determine gameType
       └─> Render appropriate component:
           ├─> TicTacToe (if gameType === 'tic_tac_toe')
           └─> ConnectFour (if gameType === 'connect_four')

2. Game Component (e.g., TicTacToe):
   └─> useGameSession hook:
       ├─> Initial fetch
       └─> Polling (stops when game ends)
   
   └─> Turn Management:
       ├─> Check: session.currentTurn === user.id
       ├─> Disable board if not user's turn
       └─> Enable board if user's turn

3. User makes move:
   └─> Click cell/column
       └─> POST /api/sessions/{sessionId}/move
           ├─> Success → Polling updates board
           └─> Error → Show toast notification

4. Game ends:
   └─> Polling stops (stopWhen condition)
       └─> Show winner/draw message
           └─> Show "Play Again" button
```

### 5. API Client Design (`utils/api.ts`)

**Features**:
- Base URL configuration (env variable)
- Error handling
- Type-safe responses (TypeScript)
- Polling utility with cancellation

**Key Functions**:
```typescript
createUser(name, icon?)
createSession(payload)
getSession(sessionId)
joinSession(sessionId, playerId)
makeMove(sessionId, playerId, row, col)
listSessions(params?)
pollSession(sessionId, callback, options)
```

### 6. Next.js API Proxy

**Configuration** (`next.config.js`):
```javascript
async rewrites() {
  return [{
    source: '/api/:path*',
    destination: `${API_PROXY_TARGET}/:path*`
  }]
}
```

**Why**: 
- Frontend calls `/api/*` (relative URLs)
- Next.js proxies to backend
- Simplifies CORS, allows different ports in dev

---

## Key Flows & Use Cases

### Flow 1: Complete Game Lifecycle

```
┌─────────┐
│  User 1 │ Creates Session
└────┬────┘
     │ POST /sessions
     ▼
┌─────────────┐
│  Backend    │ Creates Session (WAITING)
└────┬────────┘
     │ Returns sessionId
     ▼
┌─────────────┐
│  User 1     │ Redirected to /waiting/{sessionId}
└────┬────────┘
     │ Shares link
     ▼
┌─────────────┐
│  User 2     │ Visits /join/{sessionId}
└────┬────────┘
     │ POST /sessions/{id}/join
     ▼
┌─────────────┐
│  Backend    │ Updates Session (ACTIVE)
└────┬────────┘
     │ Both users redirected to /game/{sessionId}
     ▼
┌─────────────┐
│  Both Users │ Polling starts, game begins
└────┬────────┘
     │
     │ User 1: POST /sessions/{id}/move (row=0, col=0)
     │ User 2: POST /sessions/{id}/move (row=0, col=1)
     │ ... (alternating turns)
     │
     ▼
┌─────────────┐
│  Backend    │ Detects winner/draw
└────┬────────┘
     │ Status = FINISHED
     ▼
┌─────────────┐
│  Both Users │ Polling stops, see result
└─────────────┘
```

### Flow 2: Move Validation & State Update

```
User clicks cell
    │
    ▼
Frontend: Check if user's turn
    │
    ├─> Not user's turn → Disabled (no API call)
    │
    └─> User's turn → POST /sessions/{id}/move
            │
            ▼
        Backend: Validate move
            │
            ├─> Invalid → 400 Error
            │   └─> Frontend shows error toast
            │
            └─> Valid → Update board
                    │
                    ├─> Check winner
                    ├─> Check draw
                    ├─> Switch current_turn
                    ├─> Save Move record
                    └─> Return updated session
                            │
                            ▼
                        Frontend: Polling picks up change
                            │
                            └─> UI updates automatically
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    icon VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Sessions Table
```sql
CREATE TABLE sessions (
    id VARCHAR PRIMARY KEY,
    host_id VARCHAR NOT NULL REFERENCES users(id),
    host_name VARCHAR NOT NULL,
    host_icon VARCHAR,
    guest_id VARCHAR REFERENCES users(id),
    guest_name VARCHAR,
    guest_icon VARCHAR,
    game_type VARCHAR NOT NULL DEFAULT 'tic_tac_toe',
    game_icon VARCHAR,
    status VARCHAR NOT NULL DEFAULT 'WAITING',
    current_turn VARCHAR,
    board TEXT,  -- JSON string
    winner VARCHAR,
    draw BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Moves Table
```sql
CREATE TABLE moves (
    id VARCHAR PRIMARY KEY,
    session_id VARCHAR NOT NULL REFERENCES sessions(id),
    player_id VARCHAR NOT NULL REFERENCES users(id),
    row INTEGER NOT NULL,
    col INTEGER NOT NULL,
    move_no INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Indexes**:
- `sessions.host_id`
- `sessions.guest_id`
- `sessions.status`
- `moves.session_id`

---

## API Design

### RESTful Principles

**Resources**:
- `/users` - User collection
- `/sessions` - Session collection
- `/sessions/{id}` - Individual session
- `/sessions/{id}/join` - Join action
- `/sessions/{id}/move` - Move action

**HTTP Methods**:
- `GET`: Read operations
- `POST`: Create operations, actions
- No PUT/PATCH/DELETE (not needed for MVP)

**Status Codes**:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Server Error

### Request/Response Examples

**Create Session**:
```http
POST /sessions
Content-Type: application/json

{
  "hostId": "user-123",
  "hostName": "Alice",
  "gameType": "tic_tac_toe",
  "gameIcon": "🎮"
}

Response: 201 Created
{
  "id": "session-abc",
  "players": [{"id": "user-123", "name": "Alice"}],
  "status": "WAITING",
  "board": [[null, null, null], ...],
  "gameType": "tic_tac_toe",
  ...
}
```

**Make Move**:
```http
POST /sessions/session-abc/move
Content-Type: application/json

{
  "playerId": "user-123",
  "row": 1,
  "col": 1
}

Response: 200 OK
{
  "id": "session-abc",
  "currentTurn": "user-456",
  "board": [[null, null, null], [null, "user-123", null], ...],
  ...
}
```

---

## Design Decisions & Trade-offs

### 1. Extensible Game Logic System

**Decision**: Strategy pattern with factory function

**Why**:
- Easy to add new games (Connect Four, Chess, etc.)
- Game-specific logic isolated
- Backend doesn't need to know game rules

**Trade-off**:
- Slight overhead vs. hardcoded logic
- Worth it for maintainability

### 2. Polling vs. WebSockets

**Decision**: HTTP polling with smart stop conditions

**Why**:
- Simpler implementation
- No persistent connections
- Works with standard HTTP infrastructure
- Added timeout (3 min) and stop conditions

**Trade-off**:
- Higher latency (1.2s interval)
- More HTTP requests
- For real-time games, WebSockets would be better

### 3. Board Storage: JSON vs. Normalized

**Decision**: Store board as JSON string in `sessions.board`

**Why**:
- Simple to serialize/deserialize
- Game-agnostic (works for any 2D grid)
- Single field vs. separate table

**Trade-off**:
- Can't query board state in SQL
- For complex queries, normalized would be better

### 4. Move Audit Trail

**Decision**: Separate `moves` table

**Why**:
- Enables replay, history, debugging
- Can reconstruct board from moves
- Useful for analytics

**Trade-off**:
- Extra storage
- Extra queries (when loading session)

### 5. No Authentication

**Decision**: Simple user ID in localStorage

**Why**:
- MVP simplicity
- No session management
- Fast to implement

**Trade-off**:
- Not secure (anyone can use any user ID)
- Production would need JWT/OAuth

### 6. Row-Level Locking

**Decision**: `SELECT ... FOR UPDATE` for critical operations

**Why**:
- Prevents race conditions
- Simple to implement
- Works with PostgreSQL

**Trade-off**:
- Slight performance impact
- Better than application-level locks

### 7. Frontend: Polling with Timeout

**Decision**: Polling stops after 3 minutes or when game ends

**Why**:
- Prevents infinite polling
- Saves resources
- Better UX (no unnecessary requests)

**Implementation**:
```typescript
pollSession(sessionId, callback, {
  maxDurationMs: 3 * 60 * 1000,
  stopWhen: (session) => session?.status === 'FINISHED'
})
```

---

## Key Interview Talking Points

### Backend (70%)

1. **Extensibility**: Game logic system allows easy addition of new games
2. **Concurrency**: Row-level locking prevents race conditions
3. **Validation**: Multi-layer validation (Pydantic, game logic, business rules)
4. **Database Design**: Normalized users/moves, denormalized board state
5. **Error Handling**: Proper HTTP status codes, descriptive error messages
6. **Migrations**: Alembic for version-controlled schema changes

### Frontend (30%)

1. **State Management**: React hooks + Context API (no Redux needed)
2. **Polling Strategy**: Smart polling with timeout and stop conditions
3. **Type Safety**: TypeScript throughout
4. **Component Architecture**: Small, focused components
5. **User Experience**: Disabled states, loading indicators, error toasts

### System Design

1. **Scalability**: Stateless backend, can horizontally scale
2. **Reliability**: Database transactions, error handling
3. **Maintainability**: Clear separation of concerns, extensible design
4. **Performance**: Efficient queries, polling optimization

---

## Questions to Prepare For

### Backend Questions

1. **"How would you scale this system?"**
   - Horizontal scaling (multiple FastAPI instances)
   - Database connection pooling
   - Redis for session caching
   - WebSockets for real-time updates

2. **"How do you handle concurrent moves?"**
   - Row-level locking (`SELECT ... FOR UPDATE`)
   - Transaction isolation
   - Validation before state change

3. **"How would you add a new game type?"**
   - Create new `GameLogic` subclass
   - Register in factory function
   - No changes to API or database schema

4. **"How do you ensure data consistency?"**
   - Database transactions
   - Foreign key constraints
   - Validation at multiple layers

### Frontend Questions

1. **"Why polling instead of WebSockets?"**
   - Simpler for MVP
   - No persistent connections
   - Added timeout to prevent infinite polling

2. **"How do you handle turn-based interactions?"**
   - Check `currentTurn === user.id`
   - Disable UI when not user's turn
   - Server validates anyway (security)

3. **"How do you manage state?"**
   - React hooks (useState, useEffect)
   - Context API for user state
   - Custom hooks for session state

---

## Running the System

### Backend
```bash
cd server/py3
source .venv/bin/activate
uvicorn main:app --reload
```

### Frontend
```bash
cd webapp/grid-react
pnpm install
pnpm dev
```

### Database
- Uses Supabase (PostgreSQL)
- Connection via `DATABASE_URL` env variable
- Migrations: `alembic upgrade head`

---

## Summary

This is a **two-player grid game platform** with:
- **Extensible backend** supporting multiple game types
- **Real-time updates** via polling
- **Race condition prevention** via database locking
- **Clean separation** between frontend and backend
- **Type-safe** TypeScript frontend
- **RESTful API** design

The system demonstrates:
- ✅ Backend: API design, database modeling, concurrency handling
- ✅ Frontend: State management, polling, user experience
- ✅ System: Scalability considerations, trade-offs, extensibility

