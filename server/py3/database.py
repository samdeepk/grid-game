"""Database configuration and session management."""
import os
from typing import AsyncGenerator, Optional

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# Load environment variables
load_dotenv()

# Database URLs
def _ensure_asyncpg_url(url: Optional[str]) -> str:
    """Ensure URL uses asyncpg driver and remove unsupported parameters."""
    if url is None:
        raise ValueError(
            'DATABASE_URL or DIRECT_URL is not set in .env file. Please create .env file with your database credentials.'
        )
    
    # Check if password placeholder is still in URL
    if '[YOUR-PASSWORD]' in url:
        raise ValueError(
            'Please replace [YOUR-PASSWORD] with your actual Supabase password in .env file'
        )
    
    # Remove pgbouncer parameter as asyncpg doesn't support it
    # Do this with string replacement to avoid breaking password encoding
    if '?pgbouncer=true' in url:
        url = url.replace('?pgbouncer=true', '')
    elif '?pgbouncer=false' in url:
        url = url.replace('?pgbouncer=false', '')
    elif '&pgbouncer=true' in url:
        url = url.replace('&pgbouncer=true', '')
    elif '&pgbouncer=false' in url:
        url = url.replace('&pgbouncer=false', '')
    # Handle other pgbouncer parameter formats
    elif 'pgbouncer=' in url:
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params.pop('pgbouncer', None)
        new_query = urlencode(query_params, doseq=True)
        # Preserve everything except the query
        url = urlunparse(parsed._replace(query=new_query))
    
    # Ensure asyncpg driver
    if url.startswith('postgresql://'):
        return url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    elif url.startswith('postgresql+psycopg2://'):
        return url.replace('postgresql+psycopg2://', 'postgresql+asyncpg://', 1)
    elif not url.startswith('postgresql+asyncpg://'):
        # If it doesn't start with any known prefix, assume it needs asyncpg
        if '://' in url:
            parts = url.split('://', 1)
            return f'postgresql+asyncpg://{parts[1]}'
    return url


# Get URLs from environment
# For local development, use: postgresql+asyncpg://gridgame:gridgame123@localhost:5432/gridgame
# Run: ./setup-local-db.sh to set up local PostgreSQL
DATABASE_URL_ENV = os.getenv('DATABASE_URL')
DIRECT_URL_ENV = os.getenv('DIRECT_URL')

# Use DATABASE_URL for DIRECT_URL if not set (common for local development)
if not DIRECT_URL_ENV and DATABASE_URL_ENV:
    DIRECT_URL_ENV = DATABASE_URL_ENV

if not DATABASE_URL_ENV:
    raise ValueError(
        'DATABASE_URL is not set in .env file.\n\n'
        'For local development:\n'
        '  1. Run: ./setup-local-db.sh\n'
        '  2. Or set: DATABASE_URL=postgresql+asyncpg://gridgame:gridgame123@localhost:5432/gridgame\n\n'
        'For production:\n'
        '  DATABASE_URL="postgresql+asyncpg://user:password@host:port/database"'
    )

if not DIRECT_URL_ENV:
    raise ValueError(
        'DIRECT_URL is not set in .env file.\n\n'
        'For local development, DIRECT_URL can be the same as DATABASE_URL.\n'
        'For production, set DIRECT_URL to your direct database connection URL.'
    )

DATABASE_URL = _ensure_asyncpg_url(DATABASE_URL_ENV)
DIRECT_URL = _ensure_asyncpg_url(DIRECT_URL_ENV)

# Check if using pgbouncer (typically port 6543)
# pgbouncer doesn't support prepared statements, so we need to disable statement caching
is_pgbouncer = ':6543' in DATABASE_URL_ENV or 'pooler.supabase.com' in DATABASE_URL_ENV

# Create async engine
# Note: Make sure your .env file has the correct password set
# The password should be URL-encoded if it contains special characters
connect_args = {
    'server_settings': {
        'application_name': 'grid-game',
    },
}

# Disable statement caching when using pgbouncer
# pgbouncer in transaction/statement pooling mode doesn't support prepared statements
# Setting statement_cache_size to 0 disables asyncpg's prepared statement cache
if is_pgbouncer:
    connect_args['statement_cache_size'] = 0
    print('⚠️  pgbouncer detected: Disabling prepared statement cache (statement_cache_size=0)')

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,
    max_overflow=20,
    connect_args=connect_args,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    Use this in FastAPI route dependencies.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        # Re-raise with more context
        raise ConnectionError(
            f'Failed to connect to database: {e}\n'
            'This is often caused by:\n'
            '1. Incorrect password in .env file\n'
            '2. Password with special characters that need URL encoding\n'
            '3. Network/firewall issues\n'
            '4. Supabase database not accessible\n'
            'Run: python test_connection.py to test your connection'
        ) from e


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()

