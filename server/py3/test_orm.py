"""Test ORM operations with SQLAlchemy."""
import asyncio
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import AsyncSessionLocal, init_db, close_db
from models import User, Game


async def test_insert_user(name: str, icon: str = None) -> User:
    """Insert a new user using ORM."""
    async with AsyncSessionLocal() as session:
        user = User(
            id=str(uuid.uuid4()),
            name=name,
            icon=icon
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"✅ Inserted user: {user}")
        return user


async def test_query_all_users() -> list[User]:
    """Query all users using ORM."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).order_by(User.created_at.desc()))
        users = result.scalars().all()
        print(f"\n📋 Found {len(users)} users:")
        for user in users:
            print(f"  - {user.name} (ID: {user.id[:8]}..., Icon: {user.icon or 'None'})")
        return users


async def test_query_user_by_id(user_id: str) -> User | None:
    """Query a specific user by ID using ORM."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            print(f"✅ Found user: {user}")
        else:
            print(f"❌ User with ID {user_id} not found")
        return user


async def test_insert_game(user_id: str, name: str, icon: str = None, status: str = 'active') -> Game:
    """Insert a new game using ORM."""
    async with AsyncSessionLocal() as session:
        game = Game(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            icon=icon,
            status=status
        )
        session.add(game)
        await session.commit()
        await session.refresh(game)
        print(f"✅ Inserted game: {game}")
        return game


async def test_query_games(user_id: str = None) -> list[Game]:
    """Query games using ORM, optionally filtered by user_id."""
    async with AsyncSessionLocal() as session:
        if user_id:
            result = await session.execute(
                select(Game)
                .where(Game.user_id == user_id)
                .order_by(Game.created_at.desc())
            )
        else:
            result = await session.execute(
                select(Game).order_by(Game.created_at.desc())
            )
        games = result.scalars().all()
        print(f"\n🎮 Found {len(games)} games:")
        for game in games:
            print(f"  - {game.name} (ID: {game.id[:8]}..., Status: {game.status}, User: {game.user_id[:8]}...)")
        return games


async def test_query_games_with_users() -> list:
    """Query games with user information using ORM relationships."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Game, User)
            .join(User, Game.user_id == User.id)
            .order_by(Game.created_at.desc())
        )
        results = result.all()
        print(f"\n🎮👤 Found {len(results)} games with user info:")
        for game, user in results:
            print(f"  - Game: {game.name} (Status: {game.status})")
            print(f"    User: {user.name} (ID: {user.id[:8]}...)")
        return results


async def test_query_user_with_games(user_id: str) -> User | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User)
            .options(selectinload(User.games))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            print(f"✅ Found user: {user.name}")
            print(f"   Games: {len(user.games)}")
            for game in user.games:
                print(f"     - {game.name} (Status: {game.status})")
        else:
            print(f"❌ User with ID {user_id} not found")
        return user


async def test_update_user(user_id: str, new_name: str = None, new_icon: str = None) -> User | None:
    """Update a user using ORM."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            if new_name:
                user.name = new_name
            if new_icon:
                user.icon = new_icon
            await session.commit()
            await session.refresh(user)
            print(f"✅ Updated user: {user}")
        else:
            print(f"❌ User with ID {user_id} not found")
        return user


async def test_delete_game(game_id: str) -> bool:
    """Delete a game using ORM."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()
        if game:
            await session.delete(game)
            await session.commit()
            print(f"✅ Deleted game: {game.name}")
            return True
        else:
            print(f"❌ Game with ID {game_id} not found")
            return False


async def main():
    """Run all ORM test functions."""
    print("=" * 60)
    print("🧪 Testing ORM Operations with SQLAlchemy")
    print("=" * 60)
    
    try:
        # Initialize database (create tables if they don't exist)
        print("\n🔧 Initializing database...")
        await init_db()
        print("✅ Database initialized")
        
        # Test 1: Insert a user
        print("\n1️⃣  Testing INSERT User (ORM)")
        print("-" * 60)
        user = await test_insert_user("Test User ORM", "🎮")
        user_id = user.id
        
        # Test 2: Query all users
        print("\n2️⃣  Testing QUERY All Users (ORM)")
        print("-" * 60)
        await test_query_all_users()
        
        # Test 3: Query specific user
        print("\n3️⃣  Testing QUERY User by ID (ORM)")
        print("-" * 60)
        await test_query_user_by_id(user_id)
        
        # Test 4: Update user
        print("\n4️⃣  Testing UPDATE User (ORM)")
        print("-" * 60)
        await test_update_user(user_id, new_name="Updated User ORM", new_icon="🎯")
        
        # Test 5: Insert a game
        print("\n5️⃣  Testing INSERT Game (ORM)")
        print("-" * 60)
        game = await test_insert_game(user_id, "Test Game ORM", "🎯", "active")
        game_id = game.id
        
        # Test 6: Query games for specific user
        print("\n6️⃣  Testing QUERY Games by User ID (ORM)")
        print("-" * 60)
        await test_query_games(user_id=user_id)
        
        # Test 7: Query all games
        print("\n7️⃣  Testing QUERY All Games (ORM)")
        print("-" * 60)
        await test_query_games()
        
        # Test 8: Query games with user info (JOIN)
        print("\n8️⃣  Testing QUERY Games with Users (JOIN - ORM)")
        print("-" * 60)
        await test_query_games_with_users()
        
        # Test 9: Query user with games (relationship)
        print("\n9️⃣  Testing QUERY User with Games (Relationship - ORM)")
        print("-" * 60)
        await test_query_user_with_games(user_id)
        
        # Test 10: Delete game
        print("\n🔟 Testing DELETE Game (ORM)")
        print("-" * 60)
        await test_delete_game(game_id)
        
        print("\n" + "=" * 60)
        print("✅ All ORM tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during tests: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close database connections
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())

