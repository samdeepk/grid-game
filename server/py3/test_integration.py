"""Integration tests for frontend-to-backend API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload

from main import app
from database import Base, get_db
from models import User, Session, Move


# Test database URL (use in-memory SQLite or separate test DB)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine and session
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    """Override get_db dependency for testing."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def db_session():
    """Create a test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Clean up
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session):
    """Create a test client with database override."""
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(id="test-user-1", name="Test User", icon="🎮")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user2(db_session: AsyncSession):
    """Create a second test user."""
    user = User(id="test-user-2", name="Test User 2", icon="🎯")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestUserEndpoints:
    """Test user-related endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient):
        """Test creating a new user."""
        response = await client.post(
            "/users",
            json={"name": "Alice", "icon": "😀"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Alice"
        assert data["icon"] == "😀"
        assert "id" in data
        assert "createdAt" in data
    
    @pytest.mark.asyncio
    async def test_create_user_no_icon(self, client: AsyncClient):
        """Test creating a user without icon."""
        response = await client.post(
            "/users",
            json={"name": "Bob"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Bob"
        assert data["icon"] is None


class TestSessionEndpoints:
    """Test session-related endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_session(self, client: AsyncClient, test_user):
        """Test creating a new session."""
        response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🎮"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["status"] == "WAITING"
        assert len(data["players"]) == 1
        assert data["players"][0]["id"] == test_user.id
        assert data["board"] == [[None, None, None], [None, None, None], [None, None, None]]
        assert data["moves"] == []
        assert data["currentTurn"] is None
    
    @pytest.mark.asyncio
    async def test_create_session_user_not_found(self, client: AsyncClient):
        """Test creating session with non-existent user."""
        response = await client.post(
            "/sessions",
            json={
                "hostId": "non-existent-user",
                "gameIcon": "🎮"
            }
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_session(self, client: AsyncClient, test_user, db_session):
        """Test getting a session by ID."""
        # Create session first
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🎮"
            }
        )
        session_id = create_response.json()["id"]
        
        # Get session
        response = await client.get(f"/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["status"] == "WAITING"
    
    @pytest.mark.asyncio
    async def test_get_session_not_found(self, client: AsyncClient):
        """Test getting non-existent session."""
        response = await client.get("/sessions/non-existent-id")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_list_sessions(self, client: AsyncClient, test_user, db_session):
        """Test listing sessions."""
        # Create a few sessions
        for i in range(3):
            await client.post(
                "/sessions",
                json={
                    "hostId": test_user.id,
                    "hostName": test_user.name,
                    "gameIcon": f"🎮{i}"
                }
            )
        
        # List sessions
        response = await client.get("/sessions?hostId=" + test_user.id)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 3
    
    @pytest.mark.asyncio
    async def test_list_sessions_filter_by_status(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test listing sessions filtered by status."""
        # Create a session and join it
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🎮"
            }
        )
        session_id = create_response.json()["id"]
        
        # Join session to make it ACTIVE
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # List ACTIVE sessions
        response = await client.get("/sessions?status=ACTIVE")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["status"] == "ACTIVE"
    
    @pytest.mark.asyncio
    async def test_join_session(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test joining a session."""
        # Create session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🎮"
            }
        )
        session_id = create_response.json()["id"]
        
        # Join session
        response = await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ACTIVE"
        assert len(data["players"]) == 2
        assert data["currentTurn"] == test_user.id  # Host goes first
        assert data["players"][1]["id"] == test_user2.id
    
    @pytest.mark.asyncio
    async def test_join_session_not_found(self, client: AsyncClient, test_user2):
        """Test joining non-existent session."""
        response = await client.post(
            "/sessions/non-existent-id/join",
            json={"playerId": test_user2.id}
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_join_session_already_full(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test joining a session that already has a guest."""
        # Create session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🎮"
            }
        )
        session_id = create_response.json()["id"]
        
        # Join as first guest
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Try to join again (should fail)
        user3 = User(id="test-user-3", name="User 3", icon="🎲")
        db_session.add(user3)
        await db_session.commit()
        
        response = await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": user3.id}
        )
        assert response.status_code == 400


class TestMoveEndpoints:
    """Test move-related endpoints."""
    
    @pytest.mark.asyncio
    async def test_make_move(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test making a move in an active session."""
        # Create and join session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🎮"
            }
        )
        session_id = create_response.json()["id"]
        
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Make a move (host's turn)
        response = await client.post(
            f"/sessions/{session_id}/move",
            json={
                "playerId": test_user.id,
                "row": 0,
                "col": 0
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["board"][0][0] == test_user.id
        assert len(data["moves"]) == 1
        assert data["moves"][0]["playerId"] == test_user.id
        assert data["moves"][0]["row"] == 0
        assert data["moves"][0]["col"] == 0
        assert data["currentTurn"] == test_user2.id  # Turn switched
    
    @pytest.mark.asyncio
    async def test_make_move_not_your_turn(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test making a move when it's not your turn."""
        # Create and join session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🎮"
            }
        )
        session_id = create_response.json()["id"]
        
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Try to move when it's host's turn (should fail)
        response = await client.post(
            f"/sessions/{session_id}/move",
            json={
                "playerId": test_user2.id,  # Guest trying to move
                "row": 0,
                "col": 0
            }
        )
        assert response.status_code == 409
    
    @pytest.mark.asyncio
    async def test_make_move_invalid_coordinates(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test making a move with invalid coordinates."""
        # Create and join session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🎮"
            }
        )
        session_id = create_response.json()["id"]
        
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Try invalid coordinates
        response = await client.post(
            f"/sessions/{session_id}/move",
            json={
                "playerId": test_user.id,
                "row": 5,  # Invalid
                "col": 0
            }
        )
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_make_move_cell_occupied(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test making a move to an occupied cell."""
        # Create and join session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🎮"
            }
        )
        session_id = create_response.json()["id"]
        
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Make first move
        await client.post(
            f"/sessions/{session_id}/move",
            json={
                "playerId": test_user.id,
                "row": 0,
                "col": 0
            }
        )
        
        # Try to move to same cell (should fail)
        response = await client.post(
            f"/sessions/{session_id}/move",
            json={
                "playerId": test_user2.id,
                "row": 0,
                "col": 0
            }
        )
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_win_condition(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test winning the game."""
        # Create and join session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🎮"
            }
        )
        session_id = create_response.json()["id"]
        
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Make moves to win (host wins with row)
        # Host: (0,0)
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 0, "col": 0}
        )
        # Guest: (1,0)
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user2.id, "row": 1, "col": 0}
        )
        # Host: (0,1)
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 0, "col": 1}
        )
        # Guest: (1,1)
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user2.id, "row": 1, "col": 1}
        )
        # Host: (0,2) - wins!
        response = await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 0, "col": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "FINISHED"
        assert data["winner"] == test_user.id
        assert data["currentTurn"] is None
    
    @pytest.mark.asyncio
    async def test_draw_condition(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test draw condition."""
        # Create and join session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🎮"
            }
        )
        session_id = create_response.json()["id"]
        
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Make moves that result in a draw (9 moves, no winner)
        # Pattern that ensures no one wins - alternating pattern:
        # Host: (0,0), (1,0), (2,1), (0,2), (2,2)
        # Guest: (0,1), (1,1), (1,2), (2,0)
        # This pattern prevents any row, column, or diagonal from having 3 of the same
        moves = [
            (test_user.id, 0, 0),   # Host - top-left
            (test_user2.id, 0, 1),  # Guest - top-middle
            (test_user.id, 1, 0),   # Host - middle-left
            (test_user2.id, 1, 1),  # Guest - center
            (test_user.id, 2, 1),   # Host - bottom-middle
            (test_user2.id, 1, 2),  # Guest - middle-right
            (test_user.id, 0, 2),   # Host - top-right
            (test_user2.id, 2, 0),  # Guest - bottom-left
            (test_user.id, 2, 2),   # Host - bottom-right (last move, draw)
        ]
        
        response = None
        for i, (player_id, row, col) in enumerate(moves):
            response = await client.post(
                f"/sessions/{session_id}/move",
                json={"playerId": player_id, "row": row, "col": col}
            )
            # Check each move succeeds (except if game finished on last move)
            if response.status_code != 200 and i < len(moves) - 1:
                break
        
        assert response is not None
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
        data = response.json()
        assert data["status"] == "FINISHED"
        assert data["draw"] is True
        assert data["winner"] is None


class TestEndToEndFlow:
    """Test complete game flow from start to finish."""
    
    @pytest.mark.asyncio
    async def test_complete_game_flow(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test complete flow: create user -> create session -> join -> play -> win."""
        # 1. Create users (already done via fixtures)
        
        # 2. Create session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🎮"
            }
        )
        assert create_response.status_code == 201
        session_id = create_response.json()["id"]
        
        # 3. Get session (should be WAITING)
        get_response = await client.get(f"/sessions/{session_id}")
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "WAITING"
        
        # 4. Join session
        join_response = await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        assert join_response.status_code == 200
        assert join_response.json()["status"] == "ACTIVE"
        
        # 5. List sessions (should show active session)
        list_response = await client.get(f"/sessions?hostId={test_user.id}")
        assert list_response.status_code == 200
        assert len(list_response.json()["items"]) >= 1
        
        # 6. Make moves
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 0, "col": 0}
        )
        
        # 7. Get updated session
        updated_response = await client.get(f"/sessions/{session_id}")
        assert updated_response.status_code == 200
        data = updated_response.json()
        assert data["board"][0][0] == test_user.id
        assert len(data["moves"]) == 1


class TestConnectFourEndpoints:
    """Test Connect 4 game-specific endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_connect_four_session(self, client: AsyncClient, test_user):
        """Test creating a Connect 4 session."""
        response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🔴",
                "gameType": "connect_four"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["gameType"] == "connect_four"
        # Board should be 6x7
        assert len(data["board"]) == 6
        assert len(data["board"][0]) == 7
        # All cells should be empty
        assert all(cell is None for row in data["board"] for cell in row)
    
    @pytest.mark.asyncio
    async def test_connect_four_column_drop(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test dropping a piece in a Connect 4 column."""
        # Create Connect 4 session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🔴",
                "gameType": "connect_four"
            }
        )
        session_id = create_response.json()["id"]
        
        # Join session
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Drop piece in column 0 (should land at row 5, the bottom)
        response = await client.post(
            f"/sessions/{session_id}/move",
            json={
                "playerId": test_user.id,
                "row": 5,  # Bottom row
                "col": 0   # First column
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["board"][5][0] == test_user.id
        assert data["board"][4][0] is None  # Row above should be empty
        assert len(data["moves"]) == 1
    
    @pytest.mark.asyncio
    async def test_connect_four_multiple_drops_same_column(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test dropping multiple pieces in the same column (stacking)."""
        # Create and join Connect 4 session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🔴",
                "gameType": "connect_four"
            }
        )
        session_id = create_response.json()["id"]
        
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Host drops in column 0 (row 5)
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 5, "col": 0}
        )
        
        # Guest drops in column 0 (row 4, stacks on top)
        response = await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user2.id, "row": 4, "col": 0}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["board"][5][0] == test_user.id  # Bottom piece
        assert data["board"][4][0] == test_user2.id  # Top piece
        assert data["board"][3][0] is None  # Above should be empty
    
    @pytest.mark.asyncio
    async def test_connect_four_invalid_drop_row(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test dropping a piece at wrong row (not the lowest empty row)."""
        # Create and join Connect 4 session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🔴",
                "gameType": "connect_four"
            }
        )
        session_id = create_response.json()["id"]
        
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Try to drop at row 3 when it should be row 5 (should fail)
        response = await client.post(
            f"/sessions/{session_id}/move",
            json={
                "playerId": test_user.id,
                "row": 3,  # Wrong row - should be 5
                "col": 0
            }
        )
        assert response.status_code == 400
        assert "drop" in response.json()["detail"].lower() or "row" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_connect_four_full_column(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test that dropping in a full column fails."""
        # Create and join Connect 4 session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🔴",
                "gameType": "connect_four"
            }
        )
        session_id = create_response.json()["id"]
        
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Fill column 0 (6 pieces)
        for i in range(6):
            player = test_user.id if i % 2 == 0 else test_user2.id
            row = 5 - i  # Start from bottom
            await client.post(
                f"/sessions/{session_id}/move",
                json={"playerId": player, "row": row, "col": 0}
            )
        
        # Try to drop in full column (should fail)
        response = await client.post(
            f"/sessions/{session_id}/move",
            json={
                "playerId": test_user.id,
                "row": 0,  # Top row
                "col": 0   # Full column
            }
        )
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_connect_four_win_horizontal(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test winning Connect 4 with 4 in a row horizontally."""
        # Create and join Connect 4 session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🔴",
                "gameType": "connect_four"
            }
        )
        session_id = create_response.json()["id"]
        
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Host wins horizontally: columns 0, 1, 2, 3 in row 5
        # Host: col 0
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 5, "col": 0}
        )
        # Guest: col 4 (different column)
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user2.id, "row": 5, "col": 4}
        )
        # Host: col 1
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 5, "col": 1}
        )
        # Guest: col 5
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user2.id, "row": 5, "col": 5}
        )
        # Host: col 2
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 5, "col": 2}
        )
        # Guest: col 6
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user2.id, "row": 5, "col": 6}
        )
        # Host: col 3 - wins!
        response = await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 5, "col": 3}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "FINISHED"
        assert data["winner"] == test_user.id
        assert data["currentTurn"] is None
    
    @pytest.mark.asyncio
    async def test_connect_four_win_vertical(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test winning Connect 4 with 4 in a row vertically."""
        # Create and join Connect 4 session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🔴",
                "gameType": "connect_four"
            }
        )
        session_id = create_response.json()["id"]
        
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Host wins vertically: column 0, rows 5, 4, 3, 2
        # Host: col 0, row 5
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 5, "col": 0}
        )
        # Guest: col 1, row 5
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user2.id, "row": 5, "col": 1}
        )
        # Host: col 0, row 4
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 4, "col": 0}
        )
        # Guest: col 1, row 4
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user2.id, "row": 4, "col": 1}
        )
        # Host: col 0, row 3
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 3, "col": 0}
        )
        # Guest: col 1, row 3
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user2.id, "row": 3, "col": 1}
        )
        # Host: col 0, row 2 - wins!
        response = await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 2, "col": 0}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "FINISHED"
        assert data["winner"] == test_user.id
    
    @pytest.mark.asyncio
    async def test_connect_four_win_diagonal(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test winning Connect 4 with 4 in a row diagonally."""
        # Create and join Connect 4 session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🔴",
                "gameType": "connect_four"
            }
        )
        session_id = create_response.json()["id"]
        
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Host wins diagonally (down-right): (5,0), (4,1), (3,2), (2,3)
        # Setup: Guest blocks in different columns
        # Host: col 0, row 5
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 5, "col": 0}
        )
        # Guest: col 1, row 5 (blocks but doesn't matter)
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user2.id, "row": 5, "col": 1}
        )
        # Host: col 1, row 4
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 4, "col": 1}
        )
        # Guest: col 2, row 5
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user2.id, "row": 5, "col": 2}
        )
        # Host: col 2, row 4
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 4, "col": 2}
        )
        # Guest: col 3, row 5
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user2.id, "row": 5, "col": 3}
        )
        # Host: col 2, row 3
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 3, "col": 2}
        )
        # Guest: col 4, row 5
        await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user2.id, "row": 5, "col": 4}
        )
        # Host: col 3, row 2 - wins diagonally!
        response = await client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": test_user.id, "row": 2, "col": 3}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "FINISHED"
        assert data["winner"] == test_user.id
    
    @pytest.mark.asyncio
    async def test_connect_four_draw(self, client: AsyncClient, test_user, test_user2, db_session):
        """Test Connect 4 draw condition (full board, no winner)."""
        # Create and join Connect 4 session
        create_response = await client.post(
            "/sessions",
            json={
                "hostId": test_user.id,
                "hostName": test_user.name,
                "gameIcon": "🔴",
                "gameType": "connect_four"
            }
        )
        session_id = create_response.json()["id"]
        
        await client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": test_user2.id}
        )
        
        # Fill the board in a pattern that doesn't create a winner
        # Alternate columns to prevent any 4-in-a-row
        # This is a simplified pattern - fill columns 0, 2, 4, 6 first, then 1, 3, 5
        # Pattern: Host fills even columns, Guest fills odd columns
        moves = []
        for col in [0, 2, 4, 6, 1, 3, 5]:  # Even columns first, then odd
            for row in range(5, -1, -1):  # Bottom to top
                player = test_user.id if col % 2 == 0 else test_user2.id
                moves.append((player, row, col))
        
        # Make all moves
        response = None
        for player_id, row, col in moves:
            response = await client.post(
                f"/sessions/{session_id}/move",
                json={"playerId": player_id, "row": row, "col": col}
            )
            if response.status_code != 200:
                break
        
        # Last move should result in draw
        assert response is not None
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "FINISHED"
        assert data["draw"] is True
        assert data["winner"] is None

