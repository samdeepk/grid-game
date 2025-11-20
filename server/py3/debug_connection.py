"""Simple psycopg2 connectivity check for Supabase/Postgres."""
from __future__ import annotations

import os
from typing import Dict, Optional

import psycopg2
from dotenv import load_dotenv
from psycopg2 import OperationalError
from sqlalchemy.engine import make_url

load_dotenv()


def _normalize_url(url: str) -> str:
    """Convert SQLAlchemy async URLs to a psycopg2-compatible scheme."""
    if url.startswith('postgresql+asyncpg://'):
        return url.replace('postgresql+asyncpg://', 'postgresql://', 1)
    if url.startswith('postgresql+psycopg2://'):
        return url.replace('postgresql+psycopg2://', 'postgresql://', 1)
    return url


def _params_from_url(url: str) -> Dict[str, str]:
    parsed = make_url(_normalize_url(url))
    if not parsed.username or not parsed.password:
        raise ValueError('Database URL must include username and password.')
    return {
        'user': parsed.username,
        'password': parsed.password,
        'host': parsed.host or 'localhost',
        'port': str(parsed.port or 5432),
        'dbname': parsed.database,
    }


def _get_first_env_value(*keys: str) -> Optional[str]:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return None


def _params_from_components() -> Optional[Dict[str, str]]:
    user = _get_first_env_value('DATABASE_USER', 'POSTGRES_USER', 'DB_USER', 'PGUSER', 'user')
    password = _get_first_env_value('DATABASE_PASSWORD', 'POSTGRES_PASSWORD', 'DB_PASSWORD', 'PGPASSWORD', 'password')
    host = _get_first_env_value('DATABASE_HOST', 'POSTGRES_HOST', 'DB_HOST', 'PGHOST', 'host')
    port = _get_first_env_value('DATABASE_PORT', 'POSTGRES_PORT', 'DB_PORT', 'PGPORT', 'port') or '5432'
    dbname = _get_first_env_value('DATABASE_NAME', 'POSTGRES_DB', 'DB_NAME', 'PGDATABASE', 'dbname')

    if not all([user, password, host, dbname]):
        return None

    return {'user': user, 'password': password, 'host': host, 'port': port, 'dbname': dbname}


def build_connection_kwargs() -> Dict[str, str]:
    url = os.getenv('DIRECT_URL') or os.getenv('DATABASE_URL')
    if url:
        try:
            return _params_from_url(url)
        except Exception as exc:
            raise RuntimeError(f'Failed to parse DATABASE_URL/DIRECT_URL: {exc}') from exc

    params = _params_from_components()
    if params:
        return params

    raise RuntimeError(
        'Could not determine connection settings. Set DATABASE_URL or define\n'
        'user/password/host/port/dbname (or their DB_/POSTGRES_/PG* variants).'
    )


def main() -> None:
    params = build_connection_kwargs()
    safe_params = params.copy()
    safe_params['password'] = '***redacted***'
    print('Attempting to connect with:', safe_params)

    try:
        with psycopg2.connect(**params) as connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT NOW();')
                current_time = cursor.fetchone()
                print('Connection successful!')
                print('Current Time:', current_time[0])
    except OperationalError as exc:
        print('Failed to connect:', exc)
        raise


if __name__ == '__main__':
    main()

