import os
import time
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load env vars from .env
load_dotenv()

def convert_asyncpg_url_to_psycopg2(url: str) -> str:
    """
    Convert SQLAlchemy asyncpg URL format to standard PostgreSQL URL for psycopg2.
    
    Converts: postgresql+asyncpg://user:pass@host:port/db
    To:       postgresql://user:pass@host:port/db
    """
    if not url:
        return url
    
    # Remove the +asyncpg part if present
    if url.startswith('postgresql+asyncpg://'):
        url = url.replace('postgresql+asyncpg://', 'postgresql://', 1)
    elif url.startswith('postgresql+psycopg2://'):
        url = url.replace('postgresql+psycopg2://', 'postgresql://', 1)
    
    return url

DATABASE_URL = os.getenv("DATABASE_URL")

def connect_with_retries(max_retries=5, base_delay=1.0):
    """
    Connect to PostgreSQL with retry logic.
    Converts asyncpg URL format to standard PostgreSQL format for psycopg2.
    """
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Convert asyncpg URL to standard PostgreSQL URL for psycopg2
    pg_url = convert_asyncpg_url_to_psycopg2(DATABASE_URL)
    
    attempt = 0
    while True:
        try:
            conn = psycopg2.connect(pg_url, cursor_factory=RealDictCursor)
            return conn
        except psycopg2.OperationalError as e:
            attempt += 1
            if attempt > max_retries:
                raise
            delay = base_delay * (2 ** (attempt - 1))
            print(f"Connection failed (attempt {attempt}/{max_retries}): {e}. Retrying in {delay:.1f}s...")
            time.sleep(delay)

def main():
    with connect_with_retries() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT now();")
            print(cur.fetchone())

if __name__ == "__main__":
    main()