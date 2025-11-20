# Database Migrations Guide

This project uses Alembic for database migrations to manage schema changes.

## Setup

Migrations are already configured. The Alembic configuration:
- Uses environment variables (`DATABASE_URL` or `DIRECT_URL`) for database connection
- Automatically converts asyncpg URLs to psycopg2 for migrations
- Supports async SQLAlchemy models

## Migration Files

Migrations are stored in `alembic/versions/` directory.

### Current Migration

**`a7d81bd218f6_add_game_state_fields_to_sessions_and_.py`**
- Adds game state fields to `sessions` table:
  - `game_type` (default: 'tic_tac_toe')
  - `guest_id`, `guest_name`, `guest_icon` (for second player)
  - `board` (JSON/Text for game state)
  - `winner` (player ID who won)
  - `draw` (boolean flag)
- Creates `moves` table for tracking game moves

## Running Migrations

### Apply Migrations (Upgrade)

```bash
cd server/py3
source .venv/bin/activate
alembic upgrade head
```

This will apply all pending migrations to bring the database to the latest schema.

### Check Migration Status

```bash
alembic current
```

Shows the current database revision.

### View Migration History

```bash
alembic history
```

Shows all available migrations.

### Rollback Migration

```bash
# Rollback one step
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

## Creating New Migrations

### Auto-generate Migration

After modifying models, create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

**Important**: Review the generated migration file before applying it. Alembic may:
- Detect changes incorrectly
- Try to drop/create tables that shouldn't be modified
- Need manual adjustments

### Manual Migration

Create an empty migration:

```bash
alembic revision -m "Description of changes"
```

Then edit the generated file in `alembic/versions/` to add your migration logic.

## Migration Best Practices

1. **Always review auto-generated migrations** before applying
2. **Test migrations** on a development database first
3. **Backup production database** before running migrations
4. **Use transactions** - Alembic runs migrations in transactions by default
5. **Add data migrations** if needed (e.g., initializing board state for existing sessions)

## Data Migration Example

If you need to migrate existing data, add it to the upgrade function:

```python
def upgrade() -> None:
    # Schema changes
    op.add_column('sessions', sa.Column('board', sa.Text(), nullable=True))
    
    # Data migration: Initialize board for existing sessions
    connection = op.get_bind()
    sessions = connection.execute(sa.text("SELECT id FROM sessions WHERE board IS NULL"))
    for session in sessions:
        default_board = json.dumps([[None, None, None], [None, None, None], [None, None, None]])
        connection.execute(
            sa.text("UPDATE sessions SET board = :board WHERE id = :id"),
            {"board": default_board, "id": session.id}
        )
```

## Troubleshooting

### Migration Fails

1. Check database connection in `.env` file
2. Ensure database user has CREATE/ALTER permissions
3. Review error message for specific issues
4. Check if migration conflicts with existing schema

### Migration Out of Sync

If your database schema doesn't match migrations:

1. **Option 1**: Create a new migration to sync current state
   ```bash
   alembic revision --autogenerate -m "Sync with current schema"
   ```

2. **Option 2**: Stamp database with current revision (if schema matches)
   ```bash
   alembic stamp head
   ```

### Reset Migrations (Development Only)

⚠️ **Warning**: Only use in development!

```bash
# Drop all tables
alembic downgrade base

# Recreate from scratch
alembic upgrade head
```

## Environment Variables

Migrations use the same database connection as the application:
- `DATABASE_URL` - Primary database URL
- `DIRECT_URL` - Direct database URL (used if DATABASE_URL not set)

The migration script automatically converts asyncpg URLs to psycopg2 for compatibility.

