# Grid-Based Game Engine - Backend Systems Challenge

A distributed grid-based game engine backend API built with FastAPI, supporting concurrent game sessions, move validation, win/draw detection, and player leaderboards.

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL (see Database Setup below)
- pip or your preferred Python package manager

### 1. Database Setup

See `server/py3/LOCAL_DEV.md` for detailed database setup instructions. Quick setup:

```bash
cd server/py3
./setup-local-db.sh
```

Or manually:
```bash
# Start PostgreSQL with Docker
docker-compose up -d

# Create .env file with:
# DATABASE_URL=postgresql+asyncpg://gridgame:gridgame123@localhost:5432/gridgame
# DIRECT_URL=postgresql+asyncpg://gridgame:gridgame123@localhost:5432/gridgame

# Run migrations
alembic upgrade head
```

### 2. Install Dependencies

```bash
cd server/py3
pip install -r requirements.txt
```

### 3. Run the API

```bash
cd server/py3
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/healthz`

### 4. Run Tests

```bash
cd server/py3
pytest test_integration.py -v
```

### 5. Run Simulation Script

The simulation script simulates multiple concurrent games and outputs a leaderboard:

```bash
cd server/py3
python simulate_games.py --players 10 --games 50 --concurrency 5
```

Options:
- `--base-url`: API base URL (default: `http://localhost:8000`)
- `--players`: Number of players (default: 10)
- `--games`: Number of games to simulate (default: 50)
- `--concurrency`: Number of concurrent games (default: 5)

Example output:
```
Creating 10 players...
✓ Created 10 players

Simulating 50 games with concurrency=5...
✓ Completed 50 games successfully

============================================================
LEADERBOARD - Top 3 Players by Win Ratio
============================================================

1. Player5 (ID: abc12345...)
   Win Ratio: 60.00%
   Wins: 3, Losses: 2, Draws: 0
   Total Games: 5
...
```

## API Endpoints

### Core Game Endpoints

- `POST /users` - Create a new player
- `POST /sessions` - Create a new game session
- `GET /sessions` - List sessions (with filtering)
- `GET /sessions/{sessionId}` - Get session state
- `POST /sessions/{sessionId}/join` - Join a session
- `POST /sessions/{sessionId}/move` - Submit a move
- `GET /leaderboard` - Get top players by win count or efficiency

### Leaderboard

```bash
# Top 3 by win count
curl http://localhost:8000/leaderboard?metric=win_count&limit=3

# Top 3 by efficiency (average moves per win, lower is better)
curl http://localhost:8000/leaderboard?metric=efficiency&limit=3
```

## Features

- ✅ Create and join game sessions
- ✅ Submit and validate moves with concurrency protection
- ✅ Detect win/draw outcomes (row, column, diagonal)
- ✅ Track per-player performance
- ✅ Leaderboard with win count and efficiency metrics
- ✅ Concurrent game simulation script
- ✅ Comprehensive test coverage

## Game Rules

- Players take turns marking a shared 3×3 grid with their unique integer ID
- A move is invalid if it's not the player's turn or the cell is already occupied
- A player wins by occupying a full row, column, or diagonal with their ID
- The game ends in a draw if all cells are filled with no winner
- Multiple game sessions can run concurrently
- Each session starts empty and becomes immutable after moves
- Once two players have joined a session, it begins

## Project Structure

```
server/py3/
├── main.py              # FastAPI application and endpoints
├── game_logic.py        # Game logic (Tic-Tac-Toe, Connect 4)
├── database.py          # Database connection and setup
├── simulate_games.py    # Concurrent game simulation script
├── test_integration.py  # Integration tests
├── models/              # SQLAlchemy models
│   ├── user.py
│   ├── session.py
│   └── move.py
└── requirements.txt     # Python dependencies
```

## Testing

Run the full test suite:

```bash
cd server/py3
pytest test_integration.py -v
```

Tests cover:
- User creation
- Session creation and joining
- Move validation and turn management
- Win/draw detection
- Error handling
- Connect 4 game logic

## Technical Details

- **Framework**: FastAPI with async/await
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Concurrency**: Row-level locking (`SELECT ... FOR UPDATE`) for move validation
- **Game Logic**: Extensible game logic system (currently supports Tic-Tac-Toe and Connect 4)

---

## Backend Deployment (Optional)

The backend can be containerized and deployed to Google Cloud Run manually or via GitHub Actions. See `server/py3/CLOUD_RUN.md` for:

- Dockerfile details and local testing instructions
- `gcloud` build/push/deploy flow (`gcloud builds submit . --file server/py3/Dockerfile ...`)
- CI/CD workflow description (`.github/workflows/backend-cloud-run.yml`) and required secrets (workflow injects the `DIRECT_URL` secret used by `server/py3/entrypoint.sh` to hydrate `/app/.env`)
- React frontend build is baked into the backend image—`pnpm run build:static` runs inside the Docker multi-stage build and the generated files are served from FastAPI (`/`), while `/healthz` exposes a JSON health probe.
