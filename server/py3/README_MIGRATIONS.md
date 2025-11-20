# Quick Migration Reference

## First Time Setup

If this is the first time setting up migrations on a database:

```bash
cd server/py3
source .venv/bin/activate

# Apply all migrations
alembic upgrade head
```

## Common Commands

```bash
# Check current migration status
alembic current

# Apply pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"
```

## Current Migration

**Revision**: `a7d81bd218f6`  
**Description**: Add game state fields to sessions and create moves table

**Changes**:
- Adds `game_type`, `guest_id`, `guest_name`, `guest_icon`, `board`, `winner`, `draw` to `sessions` table
- Creates `moves` table for tracking game moves

See `MIGRATIONS.md` for detailed documentation.

