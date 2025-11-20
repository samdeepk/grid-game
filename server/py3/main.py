"""FastAPI application with database integration."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, List
import uuid
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from sqlalchemy import select, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db, init_db
from models import Session, User, Move
from game_logic import get_game_logic


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
    
    # # Shutdown
    # try:
    #     await close_db()
    # except Exception:
    #     pass  # Ignore errors on shutdown


app = FastAPI(lifespan=lifespan)


@app.get('/healthz')
async def healthz():
    """Health probe endpoint."""
    return {'status': 'ok'}


class CreateUserRequest(BaseModel):
    name: str
    icon: Optional[str] = None


class CreateSessionRequest(BaseModel):
    hostId: str
    hostName: Optional[str] = None
    hostIcon: Optional[str] = None
    gameIcon: Optional[str] = None
    gameType: Optional[str] = 'tic_tac_toe'  # For extensibility


class JoinSessionRequest(BaseModel):
    playerId: str


class MakeMoveRequest(BaseModel):
    playerId: str
    row: int
    col: int


def serialize_session(session: Session, moves: Optional[List[Move]] = None) -> dict:
    """Serialize session into API response shape."""
    players = [
        {'id': session.host_id, 'name': session.host_name, 'icon': session.host_icon}
    ]
    
    # Add guest if exists
    if session.guest_id:
        players.append({
            'id': session.guest_id,
            'name': session.guest_name,
            'icon': session.guest_icon
        })
    
    # Get board state
    board = session.get_board()
    
    # Serialize moves
    moves_list = []
    if moves:
        moves_list = [
            {
                'playerId': move.player_id,
                'row': move.row,
                'col': move.col,
                'moveNo': move.move_no
            }
            for move in moves
        ]
    
    return {
        'id': session.id,
        'players': players,
        'status': session.status,
        'currentTurn': session.current_turn,
        'board': board,
        'moves': moves_list,
        'winner': session.winner,
        'draw': session.draw,
        'gameIcon': session.game_icon,
        'createdAt': session.created_at.isoformat() if session.created_at else None,
    }


def serialize_session_list_item(session: Session) -> dict:
    """Serialize session for list endpoint (simplified)."""
    players = [
        {'id': session.host_id, 'name': session.host_name, 'icon': session.host_icon}
    ]
    
    if session.guest_id:
        players.append({
            'id': session.guest_id,
            'name': session.guest_name,
            'icon': session.guest_icon
        })
    
    return {
        'id': session.id,
        'host': {'id': session.host_id, 'name': session.host_name, 'icon': session.host_icon},
        'gameIcon': session.game_icon,
        'status': session.status,
        'players': players,
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
    return {
        'id': user.id,
        'name': user.name,
        'icon': user.icon,
        'createdAt': user.created_at.isoformat() if user.created_at else None
    }


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

    # Initialize board for the game type
    game_logic = get_game_logic(payload.gameType or 'tic_tac_toe')
    default_board = game_logic.get_default_board()
    
    session = Session(
        id=str(uuid.uuid4()),
        host_id=host.id,
        host_name=host_name,
        host_icon=host_icon,
        game_icon=payload.gameIcon,
        game_type=payload.gameType or 'tic_tac_toe',
        status='WAITING',
        current_turn=None,
    )
    session.set_board(default_board)

    db.add(session)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    await db.refresh(session)
    return serialize_session(session)


@app.get('/sessions/{session_id}')
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get full session state."""
    result = await db.execute(
        select(Session)
        .options(selectinload(Session.moves))
        .where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Session not found'
        )
    
    return serialize_session(session, session.moves)


@app.get('/sessions')
async def list_sessions(
    status: Optional[str] = Query(None, description='Filter by status: WAITING, ACTIVE, FINISHED'),
    hostId: Optional[str] = Query(None, description='Filter by host user ID'),
    limit: int = Query(20, ge=1, le=100, description='Number of results (1-100)'),
    cursor: Optional[str] = Query(None, description='Pagination cursor'),
    db: AsyncSession = Depends(get_db)
):
    """List sessions with filtering and pagination."""
    stmt = select(Session)
    
    # Apply filters
    if status:
        if status not in ['WAITING', 'ACTIVE', 'FINISHED']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Invalid status: {status}. Must be WAITING, ACTIVE, or FINISHED'
            )
        stmt = stmt.where(Session.status == status)
    
    if hostId:
        stmt = stmt.where(Session.host_id == hostId)
    
    # Order by created_at DESC
    stmt = stmt.order_by(Session.created_at.desc())
    
    # Apply limit
    stmt = stmt.limit(limit)
    
    # Simple cursor pagination (using offset for now)
    # In production, use cursor-based pagination with session ID or timestamp
    if cursor:
        try:
            offset = int(cursor)
            stmt = stmt.offset(offset)
        except ValueError:
            pass  # Ignore invalid cursor
    
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    
    items = [serialize_session_list_item(session) for session in sessions]
    
    # Simple next cursor (offset + limit)
    next_cursor = None
    if len(items) == limit:
        current_offset = int(cursor) if cursor else 0
        next_cursor = str(current_offset + limit)
    
    return {
        'items': items,
        'nextCursor': next_cursor
    }


@app.post('/sessions/{session_id}/join', status_code=status.HTTP_200_OK)
async def join_session(
    session_id: str,
    payload: JoinSessionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Join a waiting session as the second player."""
    # Get session with row lock to prevent race conditions
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
        .with_for_update()
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Session not found'
        )
    
    # Validate session status
    if session.status != 'WAITING':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Cannot join session. Session status is {session.status}, must be WAITING'
        )
    
    # Validate user exists
    user_result = await db.execute(select(User).where(User.id == payload.playerId))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {payload.playerId} not found'
        )
    
    # Check if user is already the host
    if session.host_id == payload.playerId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User is already the host of this session'
        )
    
    # Check if session already has a guest
    if session.guest_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Session already has a guest player'
        )
    
    # Add guest player
    session.guest_id = user.id
    session.guest_name = user.name
    session.guest_icon = user.icon
    session.status = 'ACTIVE'
    session.current_turn = session.host_id  # Host goes first
    
    try:
        await db.commit()
        await db.refresh(session)
    except Exception:
        await db.rollback()
        raise
    
    # Load moves for response
    moves_result = await db.execute(
        select(Move).where(Move.session_id == session_id).order_by(Move.move_no)
    )
    moves = moves_result.scalars().all()
    
    return serialize_session(session, list(moves))


@app.post('/sessions/{session_id}/move', status_code=status.HTTP_200_OK)
async def make_move(
    session_id: str,
    payload: MakeMoveRequest,
    db: AsyncSession = Depends(get_db)
):
    """Make a move in an active session."""
    # Get session with row lock to prevent race conditions
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
        .with_for_update()
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Session not found'
        )
    
    # Validate session status
    if session.status != 'ACTIVE':
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Cannot make move. Session status is {session.status}, must be ACTIVE'
        )
    
    # Validate player is in session
    if payload.playerId != session.host_id and payload.playerId != session.guest_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Player is not part of this session'
        )
    
    # Validate it's player's turn
    if session.current_turn != payload.playerId:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='It is not your turn'
        )
    
    # Get game logic
    game_logic = get_game_logic(session.game_type)
    
    # Get current board
    board = session.get_board()
    
    # Validate move
    is_valid, error_msg = game_logic.validate_move(board, payload.row, payload.col, payload.playerId)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg or 'Invalid move'
        )
    
    # Get move count for this session
    move_count_result = await db.execute(
        select(sql_func.count(Move.id)).where(Move.session_id == session_id)
    )
    move_count = move_count_result.scalar_one() or 0
    move_no = move_count + 1
    
    # Update board
    board[payload.row][payload.col] = payload.playerId
    session.set_board(board)
    
    # Create move record
    move = Move(
        id=str(uuid.uuid4()),
        session_id=session.id,
        player_id=payload.playerId,
        row=payload.row,
        col=payload.col,
        move_no=move_no
    )
    db.add(move)
    
    # Check for winner
    winner = game_logic.check_winner(board, payload.row, payload.col, payload.playerId)
    if winner:
        session.winner = winner
        session.status = 'FINISHED'
        session.current_turn = None
    else:
        # Check for draw
        if game_logic.check_draw(board, move_no):
            session.draw = True
            session.status = 'FINISHED'
            session.current_turn = None
        else:
            # Switch turn to other player
            session.current_turn = session.guest_id if payload.playerId == session.host_id else session.host_id
    
    try:
        await db.commit()
        await db.refresh(session)
    except Exception:
        await db.rollback()
        raise
    
    # Load all moves for response
    moves_result = await db.execute(
        select(Move).where(Move.session_id == session_id).order_by(Move.move_no)
    )
    moves = moves_result.scalars().all()
    
    return serialize_session(session, list(moves))


@app.get('/leaderboard')
async def leaderboard(
    metric: str = Query('win_count', description='Sort by: win_count or efficiency'),
    limit: int = Query(3, ge=1, le=100, description='Number of top players to return (1-100)'),
    db: AsyncSession = Depends(get_db)
):
    """Get leaderboard of top players by win count or efficiency."""
    if metric not in ['win_count', 'efficiency']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Invalid metric: {metric}. Must be win_count or efficiency'
        )
    
    # Query finished sessions with winners
    finished_sessions_stmt = select(Session).where(
        Session.status == 'FINISHED',
        Session.winner.isnot(None)
    )
    finished_sessions_result = await db.execute(finished_sessions_stmt)
    finished_sessions = finished_sessions_result.scalars().all()
    
    # Calculate stats per player
    player_stats = {}  # {player_id: {'wins': count, 'total_moves': count, 'name': str}}
    
    for session in finished_sessions:
        winner_id = session.winner
        
        # Get player name from session
        if winner_id == session.host_id:
            player_name = session.host_name
        elif winner_id == session.guest_id:
            player_name = session.guest_name
        else:
            # Fallback: query User table
            user_result = await db.execute(select(User).where(User.id == winner_id))
            user = user_result.scalar_one_or_none()
            player_name = user.name if user else winner_id
        
        # Count moves in this winning game
        moves_result = await db.execute(
            select(sql_func.count(Move.id)).where(Move.session_id == session.id)
        )
        move_count = moves_result.scalar_one() or 0
        
        if winner_id not in player_stats:
            player_stats[winner_id] = {
                'wins': 0,
                'total_moves': 0,
                'name': player_name
            }
        
        player_stats[winner_id]['wins'] += 1
        player_stats[winner_id]['total_moves'] += move_count
    
    # Convert to list and calculate efficiency
    leaderboard_data = []
    for player_id, stats in player_stats.items():
        efficiency = None
        if stats['wins'] > 0:
            efficiency = stats['total_moves'] / stats['wins']
        
        leaderboard_data.append({
            'playerId': player_id,
            'name': stats['name'],
            'wins': stats['wins'],
            'efficiency': round(efficiency, 2) if efficiency is not None else None
        })
    
    # Sort by metric
    if metric == 'win_count':
        leaderboard_data.sort(key=lambda x: x['wins'], reverse=True)
    else:  # efficiency
        # Sort by efficiency (lower is better), then by wins as tiebreaker
        leaderboard_data.sort(key=lambda x: (x['efficiency'] if x['efficiency'] is not None else float('inf'), -x['wins']))
    
    # Return top N
    return leaderboard_data[:limit]


STATIC_DIR = Path(__file__).parent / 'static'
if STATIC_DIR.exists():
    app.mount('/', StaticFiles(directory=str(STATIC_DIR), html=True), name='frontend')
else:
    print('ℹ️  Frontend static bundle not found; skipping mount.')