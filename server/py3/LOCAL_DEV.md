# Local Development Setup

This guide will help you set up a local PostgreSQL database for development.

## Quick Start

1. **Run the setup script:**
   ```bash
   cd server/python
   ./setup-local-db.sh
   ```

   This will:
   - Start a PostgreSQL container using Docker
   - Create a `.env` file with local database configuration
   - Run database migrations

2. **Start the FastAPI server:**
   ```bash
   source v/bin/activate
   uvicorn main:app --reload
   ```

## Manual Setup

If you prefer to set up manually:

### 1. Start PostgreSQL with Docker

```bash
cd server/python
docker-compose up -d
```

### 2. Create .env file

Create a `.env` file in `server/python/` with:

```env
DATABASE_URL=postgresql+asyncpg://gridgame:gridgame123@localhost:5432/gridgame
DIRECT_URL=postgresql+asyncpg://gridgame:gridgame123@localhost:5432/gridgame
```

### 3. Run migrations

```bash
source v/bin/activate
alembic upgrade head
```

## Database Connection Details

- **Host:** localhost
- **Port:** 5432
- **Database:** gridgame
- **Username:** gridgame
- **Password:** gridgame123

## Docker Commands

- **Start database:** `docker-compose up -d`
- **Stop database:** `docker-compose down`
- **View logs:** `docker-compose logs -f postgres`
- **Restart database:** `docker-compose restart postgres`
- **Remove database (and data):** `docker-compose down -v`

## Troubleshooting

### Port 5432 already in use

If you have PostgreSQL running locally on port 5432, you can change the port in `docker-compose.yml`:

```yaml
ports:
  - "5433:5432"  # Use 5433 instead of 5432
```

Then update your `.env` file to use port 5433.

### Database connection errors

1. Make sure Docker is running
2. Check if the container is up: `docker ps`
3. Check container logs: `docker-compose logs postgres`
4. Verify the `.env` file has the correct connection string

### Reset database

To completely reset the database:

```bash
docker-compose down -v
./setup-local-db.sh
```

## Switching Between Local and Production

To switch back to production (Supabase), update your `.env` file with your production database URLs.

The setup script will detect if `.env` already exists and won't overwrite it, so you can safely switch between environments.

