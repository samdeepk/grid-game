#!/bin/bash

# Setup script for local PostgreSQL development
# This script sets up a local PostgreSQL database using Docker

set -e

echo "🚀 Setting up local PostgreSQL database for Grid Game..."

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Error: docker-compose is not available. Please install docker-compose."
    exit 1
fi

# Navigate to script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Start PostgreSQL container
echo "📦 Starting PostgreSQL container..."
$COMPOSE_CMD up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker exec grid-game-postgres pg_isready -U gridgame -d gridgame &> /dev/null; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Attempt $attempt/$max_attempts..."
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Error: PostgreSQL failed to start within $max_attempts seconds"
    exit 1
fi

# Check if .env file exists
ENV_FILE="$SCRIPT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "📝 Creating .env file..."
    cat > "$ENV_FILE" << EOF
# Local Development Database Configuration
DATABASE_URL=postgresql+asyncpg://gridgame:gridgame123@localhost:5432/gridgame
DIRECT_URL=postgresql+asyncpg://gridgame:gridgame123@localhost:5432/gridgame

# For production, uncomment and set these:
# DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
# DIRECT_URL=postgresql+asyncpg://user:password@host:port/database
EOF
    echo "✅ Created .env file with local database configuration"
else
    echo "⚠️  .env file already exists. Please ensure it has the correct local database URL:"
    echo "   DATABASE_URL=postgresql+asyncpg://gridgame:gridgame123@localhost:5432/gridgame"
    echo "   DIRECT_URL=postgresql+asyncpg://gridgame:gridgame123@localhost:5432/gridgame"
fi

# Run database migrations
echo "🔄 Running database migrations..."
if [ -d "$SCRIPT_DIR/v/bin" ]; then
    source "$SCRIPT_DIR/v/bin/activate"
    alembic upgrade head
    echo "✅ Database migrations completed"
else
    echo "⚠️  Virtual environment not found. Please run migrations manually:"
    echo "   source v/bin/activate"
    echo "   alembic upgrade head"
fi

echo ""
echo "🎉 Local database setup complete!"
echo ""
echo "Database connection details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: gridgame"
echo "  Username: gridgame"
echo "  Password: gridgame123"
echo ""
echo "To stop the database: docker-compose down"
echo "To start the database: docker-compose up -d"
echo "To view logs: docker-compose logs -f postgres"

