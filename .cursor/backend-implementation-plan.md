# Backend Implementation Plan

This document outlines the changes needed to implement the missing backend endpoints and functionality to support the frontend.

## Current Status

### Implemented Endpoints
- ✅ `POST /users` - Create user (needs createdAt in response)
- ✅ `POST /sessions` - Create session

### Missing Endpoints (Critical)
- ❌ `GET /sessions/{sessionId}` - Get full session state
- ❌ `POST /sessions/{sessionId}/join` - Join a session
- ❌ `POST /sessions/{sessionId}/move` - Make a move
- ❌ `GET /sessions` - List sessions with filtering

## Implementation Tasks

### 1. Database Model Updates

#### 1.1 Update Session Model
**File**: `server/py3/models/session.py`

Add fields to support game state:
- `guest_id` (String, nullable) - ID of second player
- `guest_name` (String, nullable) - Name of second player
- `guest_icon` (String, nullable) - Icon of second player
- `board` (JSON/Text) - 3x3 grid state: `[[playerId|null, ...], ...]`
- `winner` (String, nullable) - Player ID who won
- `draw` (Boolean, default=False) - Whether game ended in draw

**Note**: For PostgreSQL, use `JSON` type. For compatibility, could use `Text` and serialize/deserialize.

#### 1.2 Create Move Model
**File**: `server/py3/models/move.py` (new)

Track individual moves for audit trail:
```python
class Move(Base):
    __tablename__ = 'moves'
    
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey('sessions.id'), nullable=False)
    player_id = Column(String, ForeignKey('users.id'), nullable=False)
    row = Column(Integer, nullable=False)  # 0-2
    col = Column(Integer, nullable=False)   # 0-2
    move_no = Column(Integer, nullable=False)  # Sequential move number
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Relationships**:
- `session = relationship('Session', back_populates='moves')`
- Update Session model: `moves = relationship('Move', back_populates='session', order_by='Move.move_no')`

### 2. Serialization Functions

#### 2.1 Update serialize_session()
**File**: `server/py3/main.py`

Current function only returns basic info. Update to:
- Load board from database (deserialize JSON if stored as text)
- Load moves from Move table or deserialize from JSON
- Include winner and draw fields
- Return full player list (host + guest if exists)

**Response format**:
```python
{
    'id': session.id,
    'players': [
        {'id': session.host_id, 'name': session.host_name, 'icon': session.host_icon},
        # Add guest if exists
    ],
    'status': session.status,
    'currentTurn': session.current_turn,
    'board': [[...], [...], [...]],  # 3x3 grid
    'moves': [
        {'playerId': move.player_id, 'row': move.row, 'col': move.col, 'moveNo': move.move_no}
    ],
    'winner': session.winner,
    'draw': session.draw,
    'gameIcon': session.game_icon,
    'createdAt': session.created_at.isoformat()
}
```

#### 2.2 Create serialize_session_list_item()
**File**: `server/py3/main.py`

For list endpoint, return simplified session info:
```python
{
    'id': session.id,
    'host': {'id': session.host_id, 'name': session.host_name, 'icon': session.host_icon},
    'gameIcon': session.game_icon,
    'status': session.status,
    'players': [
        {'id': session.host_id, 'name': session.host_name, 'icon': session.host_icon},
        # Add guest if exists
    ],
    'createdAt': session.created_at.isoformat()
}
```

### 3. Endpoint Implementations

#### 3.1 GET /sessions/{sessionId}
**File**: `server/py3/main.py`

- Query session by ID
- If not found, return 404
- Load moves from Move table
- Deserialize board from JSON/text
- Return serialized session using `serialize_session()`

**Error handling**:
- 404 if session not found

#### 3.2 GET /sessions (List Sessions)
**File**: `server/py3/main.py`

**Query Parameters**:
- `status` (optional): Filter by WAITING|ACTIVE|FINISHED
- `hostId` (optional): Filter by host user ID
- `limit` (optional, default=20, max=100): Number of results
- `cursor` (optional): Pagination token (can use session ID or timestamp)

**Implementation**:
- Build query with filters
- Order by `created_at DESC`
- Apply limit
- Return `{'items': [...], 'nextCursor': ...}`

**Note**: For cursor pagination, can use last session ID or timestamp. Simple implementation: use offset/limit.

#### 3.3 POST /sessions/{sessionId}/join
**File**: `server/py3/main.py`

**Request Body**:
```json
{
  "playerId": "string"
}
```

**Logic**:
1. Validate session exists (404 if not)
2. Validate session status is WAITING (400 if not)
3. Validate user exists
4. Check if player is already host (400 if yes)
5. Check if session already has guest (400 if full)
6. Add guest player:
   - Set `guest_id`, `guest_name`, `guest_icon` from user
   - Set `status` to 'ACTIVE'
   - Set `current_turn` to `host_id` (host goes first)
7. Return updated session using `serialize_session()`

**Error handling**:
- 404: Session not found
- 400: Invalid request (session finished, already full, user is host)

#### 3.4 POST /sessions/{sessionId}/move
**File**: `server/py3/main.py`

**Request Body**:
```json
{
  "playerId": "string",
  "row": 0-2,
  "col": 0-2
}
```

**Logic** (with transaction locking):
1. Start transaction with row lock: `SELECT ... FOR UPDATE`
2. Validate session exists (404 if not)
3. Validate session status is ACTIVE (400/409 if not)
4. Validate player is in session (host or guest) (400 if not)
5. Validate it's player's turn (409 if not)
6. Validate coordinates are 0-2 (400 if invalid)
7. Validate cell is empty (409 if occupied)
8. Update board state
9. Create Move record
10. Check for winner using winner detection algorithm
11. Check for draw (9 moves, no winner)
12. Update session:
    - Set `winner` if won
    - Set `draw=True` if draw
    - Set `status='FINISHED'` if game ended
    - Set `current_turn` to other player if game continues
13. Commit transaction
14. Return updated session

**Error handling**:
- 404: Session not found
- 400: Invalid coordinates, missing fields, player not in session
- 409: Not player's turn, cell occupied, session not active

### 4. Game Logic

#### 4.1 Winner Detection Algorithm
**File**: `server/py3/main.py` (helper function)

After a move at position (row, col) by player P:
1. Check row `row`: Count moves by P in this row
2. Check column `col`: Count moves by P in this column
3. Check main diagonal (if row == col): Count moves by P
4. Check anti-diagonal (if row + col == 2): Count moves by P
5. If any count == 3, player P wins
6. Return winner player ID or None

**Implementation**:
```python
def check_winner(board: list, player_id: str, row: int, col: int) -> bool:
    # Check row
    if all(board[row][c] == player_id for c in range(3)):
        return True
    # Check column
    if all(board[r][col] == player_id for r in range(3)):
        return True
    # Check main diagonal
    if row == col and all(board[i][i] == player_id for i in range(3)):
        return True
    # Check anti-diagonal
    if row + col == 2 and all(board[i][2-i] == player_id for i in range(3)):
        return True
    return False
```

#### 4.2 Board State Management

**Initialization**: Empty 3x3 grid of None
```python
board = [[None, None, None], [None, None, None], [None, None, None]]
```

**Storage**: 
- Option A: Store as JSON in database (PostgreSQL JSON type)
- Option B: Store as text, serialize/deserialize

**Update**: After each move, update board[row][col] = player_id

#### 4.3 Turn Management

- Initial: `current_turn = host_id` (after guest joins)
- After each move: Switch to other player
- On win/draw: `current_turn = None`

### 5. Additional Updates

#### 5.1 Update POST /users Response
**File**: `server/py3/main.py`

Add `createdAt` field to response:
```python
return {
    'id': user.id,
    'name': user.name,
    'icon': user.icon,
    'createdAt': user.created_at.isoformat()
}
```

#### 5.2 Database Migration

After updating models:
1. Create migration script or
2. Drop and recreate tables (for development)
3. Update `__init__.py` in models to export Move model

### 6. Error Response Format

Follow API contract format:
- 400: `{'message': 'string', 'details': {...}}`
- 404: `{'message': 'Not found'}`
- 409: `{'message': 'Conflict - reason'}`
- 500: `{'message': 'Internal server error'}`

## Implementation Order

1. **Database Models** (Tasks 1.1, 1.2)
   - Update Session model
   - Create Move model
   - Update model exports

2. **Serialization** (Tasks 2.1, 2.2)
   - Update serialize_session()
   - Create serialize_session_list_item()

3. **Read Endpoints** (Tasks 3.1, 3.2)
   - GET /sessions/{sessionId}
   - GET /sessions (list)

4. **Write Endpoints** (Tasks 3.3, 3.4)
   - POST /sessions/{sessionId}/join
   - POST /sessions/{sessionId}/move

5. **Game Logic** (Tasks 4.1, 4.2, 4.3)
   - Winner detection
   - Board management
   - Turn management

6. **Polish** (Tasks 5.1, 5.2)
   - Update user response
   - Database migrations

## Testing Considerations

- Test session creation and serialization
- Test joining session (valid and invalid cases)
- Test making moves (valid and invalid cases)
- Test winner detection (all win conditions)
- Test draw detection
- Test concurrent moves (transaction locking)
- Test list filtering and pagination
- Test error cases (404, 400, 409)

## Notes

- Use database transactions with row locking for move endpoint to prevent race conditions
- Consider using PostgreSQL JSON type for board storage
- Moves table provides audit trail and can be used to reconstruct board state
- For production, consider adding indexes on frequently queried fields (session_id, player_id, status)

