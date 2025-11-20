"""Quick script to verify migration was applied correctly."""
import asyncio
from sqlalchemy import text
from database import engine


async def check_migration():
    """Check if migration columns exist."""
    async with engine.connect() as conn:
        # Check sessions columns
        result = await conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='sessions' ORDER BY column_name")
        )
        columns = [r[0] for r in result]
        print("Sessions table columns:")
        for col in columns:
            print(f"  - {col}")
        
        # Check for new columns
        new_columns = ['game_type', 'guest_id', 'guest_name', 'guest_icon', 'board', 'winner', 'draw']
        missing = [col for col in new_columns if col not in columns]
        if missing:
            print(f"\n⚠️  Missing columns: {missing}")
        else:
            print("\n✅ All new columns exist in sessions table")
        
        # Check moves table
        result = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name='moves'")
        )
        moves_exists = bool(list(result))
        if moves_exists:
            print("✅ Moves table exists")
        else:
            print("⚠️  Moves table does not exist")


if __name__ == "__main__":
    asyncio.run(check_migration())

