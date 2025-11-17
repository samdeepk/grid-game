"""FastAPI application with database integration."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import uuid

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import close_db, get_db, init_db
from models import Game, Session, User


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup - try to initialize DB, but don't fail if it doesn't work
    # This allows the app to start even if there are connection issues
    try:
        await init_db()
        print('✓ Database initialized successfully')
    except Exception as e:
        error_msg = str(e)
        print(f'⚠ WARNING: Failed to initialize database: {error_msg}')
        print('\nThe application will start, but database features will not work.')
        print('Please check your .env file and ensure:')
        print('1. DATABASE_URL and DIRECT_URL are set correctly')
        print('2. Your Supabase password is correct')
        print('3. If password has special characters, URL-encode them')
        print('4. Verify your Supabase database is accessible')
        print('\nYou can test the connection with: python debug_connection.py')
        # Don't raise - allow app to start without DB
    
    yield
    
    # Shutdown
    try:
        await close_db()
    except Exception:
        pass  # Ignore errors on shutdown


app = FastAPI(lifespan=lifespan)


@app.get('/')
async def read_root():
    """Root endpoint."""
    return {'Hello': 'World', 'database': 'connected'}


class CreateUserRequest(BaseModel):
    name: str
    icon: Optional[str] = None


class CreateSessionRequest(BaseModel):
    hostId: str
    hostName: Optional[str] = None
    hostIcon: Optional[str] = None
    gameIcon: Optional[str] = None


def serialize_session(session: Session) -> dict:
    """Serialize session into API response shape."""
    players = [
        {'id': session.host_id, 'name': session.host_name, 'icon': session.host_icon}
    ]
    return {
        'id': session.id,
        'players': players,
        'status': session.status,
        'currentTurn': session.current_turn,
        'board': [[None, None, None], [None, None, None], [None, None, None]],
        'moves': [],
        'winner': None,
        'draw': False,
        'gameIcon': session.game_icon,
        'createdAt': session.created_at.isoformat() if session.created_at else None,
    }


@app.post('/users', status_code=status.HTTP_201_CREATED)
async def create_user(payload: CreateUserRequest, db: AsyncSession = Depends(get_db)):
    """Create a new user using SQLAlchemy ORM."""
    user = User(id=str(uuid.uuid4()), name=payload.name, icon=payload.icon)
            
    db.add(user)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    await db.refresh(user)
    return {'id': user.id, 'name': user.name, 'icon': user.icon}


@app.post('/sessions', status_code=status.HTTP_201_CREATED)
async def create_session(payload: CreateSessionRequest, db: AsyncSession = Depends(get_db)):
    """Create a new session for the given host."""
    result = await db.execute(select(User).where(User.id == payload.hostId))
    host = result.scalar_one_or_none()
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {payload.hostId} not found',
        )

    host_name = payload.hostName or host.name
    host_icon = payload.hostIcon if payload.hostIcon is not None else host.icon

    session = Session(
        id=str(uuid.uuid4()),
        host_id=host.id,
        host_name=host_name,
        host_icon=host_icon,
        game_icon=payload.gameIcon,
        status='WAITING',
        current_turn=None,
    )

    db.add(session)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    await db.refresh(session)
    return serialize_session(session)


@app.get('/start-game')
async def start_game(
    user_id: str,
    name: str,
    icon: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Start a new game."""
    # Ensure the user exists before creating a game
    result = await db.execute(select(User.id).where(User.id == user_id))
    existing_user = result.scalar_one_or_none()
    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {user_id} not found',
        )

    game = Game(id=str(uuid.uuid4()), user_id=user_id, name=name, icon=icon, status='active')
    db.add(game)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    await db.refresh(game)
    return {'id': game.id, 'name': game.name, 'status': game.status}


@app.get('/join-game')
async def join_game():
    """Join an existing game."""
    pass


@app.get('/make-move')
async def make_move():
    """Make a move in a game."""
    pass


@app.get('/game-list')
async def game_list(user_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """Get list of games."""
    if user_id:
        stmt = select(Game).where(Game.user_id == user_id)
    else:
        stmt = select(Game)

    result = await db.execute(stmt)
    games = result.scalars().all()
    return [
        {'id': game.id, 'name': game.name, 'icon': game.icon, 'status': game.status}
        for game in games
    ]


@app.get('/leaderboard')
async def leaderboard():
    """Get leaderboard."""
    pass