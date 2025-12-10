# Grid Game - Flow Diagrams
## Visual Reference for Code Walkthrough

---

## 1. System Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Next.js    │  │   React      │  │  TypeScript  │     │
│  │   App Router │  │   Components │  │   Types      │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │              │
│         └─────────────────┼──────────────────┘              │
│                           │                                 │
│                    ┌──────▼──────┐                          │
│                    │  API Client │                          │
│                    │  (api.ts)   │                          │
│                    └──────┬──────┘                          │
└───────────────────────────┼─────────────────────────────────┘
                            │ HTTP/REST (JSON)
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      NEXT.JS PROXY                           │
│              /api/* → http://backend:8000/*                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    FASTAPI BACKEND                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routes     │  │  Game Logic  │  │  Validation  │     │
│  │  (main.py)   │  │ (game_logic) │  │  (Pydantic)  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │              │
│         └─────────────────┼──────────────────┘              │
│                           │                                 │
│                    ┌──────▼──────┐                          │
│                    │  SQLAlchemy │                          │
│                    │     ORM     │                          │
│                    └──────┬──────┘                          │
└───────────────────────────┼─────────────────────────────────┘
                            │ SQL
┌───────────────────────────▼─────────────────────────────────┐
│                    POSTGRESQL DB                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  users   │  │ sessions │  │  moves   │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Create Session Flow

```
User Action: Click "Create Game"
    │
    ▼
┌─────────────────────────────────┐
│  Frontend: CreateGameModal       │
│  - User selects game icon/type   │
└──────────────┬───────────────────┘
               │
               │ POST /api/sessions
               │ {
               │   "hostId": "user-123",
               │   "gameType": "tic_tac_toe"
               │ }
               ▼
┌─────────────────────────────────┐
│  Backend: POST /sessions         │
│  1. Validate host user exists    │
│  2. Get game logic               │
│  3. Create Session record:       │
│     - id: UUID                   │
│     - status: 'WAITING'          │
│     - board: default_board()    │
│  4. Save to DB                   │
│  5. Return serialized session    │
└──────────────┬───────────────────┘
               │
               │ 201 Created
               │ { session object }
               ▼
┌─────────────────────────────────┐
│  Frontend: Redirect              │
│  router.push('/waiting/{id}')   │
└─────────────────────────────────┘
```

---

## 3. Join Session Flow

```
User Action: Visit /join/{sessionId}
    │
    ▼
┌─────────────────────────────────┐
│  Frontend: JoinPageClient        │
│  - Fetch session                 │
│  - Show join button              │
└──────────────┬───────────────────┘
               │
               │ User clicks "Join"
               │ POST /api/sessions/{id}/join
               │ { "playerId": "user-456" }
               ▼
┌─────────────────────────────────┐
│  Backend: POST /sessions/{id}/join│
│                                   │
│  WITH ROW LOCK:                  │
│  SELECT * FROM sessions          │
│  WHERE id = ? FOR UPDATE         │
│                                   │
│  Validations:                    │
│  ✓ Session exists?               │
│  ✓ Status == 'WAITING'?          │
│  ✓ User exists?                  │
│  ✓ Not already host?             │
│  ✓ guest_id is null?             │
│                                   │
│  Updates:                        │
│  - guest_id = user-456           │
│  - status = 'ACTIVE'             │
│  - current_turn = host_id        │
│                                   │
│  COMMIT TRANSACTION              │
└──────────────┬───────────────────┘
               │
               │ 200 OK
               │ { updated session }
               ▼
┌─────────────────────────────────┐
│  Frontend: Redirect              │
│  router.push('/game/{id}')      │
└─────────────────────────────────┘
```

---

## 4. Make Move Flow (Backend Focus)

```
User clicks cell/column
    │
    ▼
┌─────────────────────────────────┐
│  Frontend: Check turn            │
│  if (currentTurn !== userId)     │
│    return; // Disabled           │
└──────────────┬───────────────────┘
               │
               │ POST /api/sessions/{id}/move
               │ {
               │   "playerId": "user-123",
               │   "row": 1,
               │   "col": 1
               │ }
               ▼
┌─────────────────────────────────┐
│  Backend: POST /sessions/{id}/move│
│                                   │
│  STEP 1: Load with lock          │
│  SELECT * FROM sessions          │
│  WHERE id = ? FOR UPDATE         │
│                                   │
│  STEP 2: Validate                │
│  ✓ status == 'ACTIVE'?            │
│  ✓ current_turn == playerId?     │
│  ✓ Load board (JSON → array)     │
│  ✓ Get game logic                │
│  ✓ game_logic.validate_move()    │
│                                   │
│  STEP 3: Apply move              │
│  board[row][col] = playerId      │
│                                   │
│  STEP 4: Check game state        │
│  winner = game_logic.check_winner()│
│  draw = game_logic.check_draw()  │
│                                   │
│  STEP 5: Update session          │
│  - Save board (array → JSON)     │
│  - current_turn = other_player   │
│  - winner = winner (if any)      │
│  - draw = draw                   │
│  - status = 'FINISHED' (if done) │
│                                   │
│  STEP 6: Create move record      │
│  INSERT INTO moves (...)         │
│                                   │
│  COMMIT TRANSACTION              │
└──────────────┬───────────────────┘
               │
               │ 200 OK
               │ { updated session }
               ▼
┌─────────────────────────────────┐
│  Frontend: Polling picks up      │
│  - Board updates                 │
│  - Turn indicator changes        │
│  - Winner/draw shown             │
└─────────────────────────────────┘
```

---

## 5. Polling Flow (Frontend Focus)

```
Component mounts (e.g., TicTacToe)
    │
    ▼
┌─────────────────────────────────┐
│  useGameSession hook             │
│  1. Initial fetch                │
│     getSession(sessionId)        │
│  2. Start polling               │
│     pollSession(sessionId, ...) │
└──────────────┬───────────────────┘
               │
               │ Every 1.2 seconds
               ▼
┌─────────────────────────────────┐
│  Polling Loop                    │
│                                   │
│  while (!cancelled &&            │
│        !timeout &&               │
│        !stopCondition) {         │
│                                   │
│    GET /api/sessions/{id}        │
│    callback(session)              │
│                                   │
│    if (stopWhen(session))         │
│      break;                       │
│                                   │
│    setTimeout(tick, 1200ms)      │
│  }                                │
└──────────────┬───────────────────┘
               │
               │ Updates state
               ▼
┌─────────────────────────────────┐
│  Component re-renders            │
│  - Board updates                 │
│  - Turn indicator                │
│  - Game status                   │
└─────────────────────────────────┘

Stop Conditions:
- Game finished (winner/draw)
- 3 minutes elapsed
- Component unmounts
```

---

## 6. Game Logic Extensibility

```
┌─────────────────────────────────┐
│  GameLogic (Abstract Base)      │
│  - get_default_board()          │
│  - validate_move()              │
│  - check_winner()               │
│  - check_draw()                 │
└──────────────┬──────────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
┌─────────────┐  ┌─────────────┐
│ TicTacToe   │  │ ConnectFour │
│ Logic       │  │ Logic       │
│             │  │             │
│ 3x3 board   │  │ 6x7 board   │
│ Check 3 in  │  │ Check 4 in  │
│ a row       │  │ a row       │
└─────────────┘  └─────────────┘

Factory Function:
get_game_logic(game_type)
    │
    ├─> 'tic_tac_toe' → TicTacToeLogic()
    ├─> 'connect_four' → ConnectFourLogic()
    └─> default → TicTacToeLogic()

Usage in Backend:
game_logic = get_game_logic(session.game_type)
board = game_logic.get_default_board()
is_valid, error = game_logic.validate_move(...)
winner = game_logic.check_winner(...)
```

---

## 7. Database Transaction Flow

```
┌─────────────────────────────────┐
│  BEGIN TRANSACTION               │
│  (Automatic in FastAPI)          │
└──────────────┬───────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  ACQUIRE ROW LOCK                │
│  SELECT ... FOR UPDATE           │
│  (Blocks other transactions)     │
└──────────────┬───────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  VALIDATE                        │
│  - Business rules                │
│  - Game rules                    │
└──────────────┬───────────────────┘
               │
               ├─> Invalid → ROLLBACK
               │
               └─> Valid
                   │
                   ▼
┌─────────────────────────────────┐
│  UPDATE DATA                     │
│  - Modify session                │
│  - Create move record            │
└──────────────┬───────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  COMMIT TRANSACTION              │
│  (Releases lock)                 │
└─────────────────────────────────┘
```

---

## 8. Error Handling Flow

```
API Request
    │
    ▼
┌─────────────────────────────────┐
│  Backend Validation              │
└──────────────┬───────────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
┌─────────────┐  ┌─────────────┐
│  Valid      │  │  Invalid    │
└──────┬──────┘  └──────┬──────┘
       │                │
       │                ▼
       │        ┌─────────────────┐
       │        │  HTTPException  │
       │        │  status_code    │
       │        │  detail         │
       │        └────────┬────────┘
       │                 │
       │                 │ 400/404/500
       │                 ▼
       │        ┌─────────────────┐
       │        │  Frontend       │
       │        │  catch error    │
       │        │  show toast     │
       │        └─────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Process Request                 │
│  Return 200/201                  │
└─────────────────────────────────┘
```

---

## 9. State Synchronization

```
┌─────────────────────────────────┐
│  User 1 makes move               │
│  POST /sessions/{id}/move        │
└──────────────┬───────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Backend updates session         │
│  - Board state                   │
│  - current_turn                  │
└──────────────┬───────────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
┌─────────────┐  ┌─────────────┐
│  User 1     │  │  User 2     │
│  (Immediate)│  │  (Polling)  │
│             │  │             │
│  Response   │  │  Next poll  │
│  received   │  │  (1.2s)     │
└─────────────┘  └─────────────┘
       │               │
       └───────┬───────┘
               │
               ▼
┌─────────────────────────────────┐
│  Both see updated state          │
│  - Board reflects move           │
│  - Turn indicator updated        │
└─────────────────────────────────┘
```

---

## 10. Component Hierarchy (Frontend)

```
App (Next.js)
│
├─> Home Page (/)
│   ├─> GameList
│   ├─> CreateGameModal
│   └─> UserNameModal
│
├─> Waiting Room (/waiting/{id})
│   └─> WaitingRoom
│       └─> useGameSession (polling)
│
└─> Game Page (/game/{id})
    └─> GamePageClient
        ├─> Fetch session
        ├─> Determine gameType
        │
        ├─> TicTacToe (if tic_tac_toe)
        │   ├─> useGameSession
        │   ├─> GameBoard
        │   ├─> GameStatus
        │   └─> PlayerInfo
        │
        └─> ConnectFour (if connect_four)
            ├─> useGameSession
            ├─> ConnectFourBoard
            ├─> GameStatus
            └─> PlayerInfo
```

---

## Key Points for Interview

### Backend (70%)

1. **Row-level locking** prevents race conditions
2. **Game logic abstraction** enables extensibility
3. **Transaction management** ensures consistency
4. **Validation layers** (Pydantic + business logic)
5. **Move audit trail** for debugging/replay

### Frontend (30%)

1. **Polling with smart stop** (timeout + conditions)
2. **Turn-based UI** (disabled when not user's turn)
3. **Type-safe API client** (TypeScript)
4. **Component composition** (small, focused)
5. **State management** (hooks + context)

### System Design

1. **Stateless backend** (scalable)
2. **RESTful API** (standard patterns)
3. **Database normalization** (users, moves)
4. **Denormalized board** (JSON for simplicity)
5. **Trade-offs documented** (polling vs WebSockets, etc.)

