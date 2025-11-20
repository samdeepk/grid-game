"""Alembic migration script for Grid Game.

Basic async-aware env that reads database URL from `.env` and uses the project's
`Base.metadata` for target metadata (models).
"""
from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool
import sqlalchemy as sa
import sys
import os as _os
# Ensure the parent project directory (server/py3) is on the Python path so local imports (like `database`) resolve
PROJECT_DIR = _os.path.dirname(_os.path.dirname(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# Load .env for local dev
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Ensure env has DB url (DIRECT_URL preferred over DATABASE_URL)
DB_URL = os.getenv('DIRECT_URL') or os.getenv('DATABASE_URL')
if not DB_URL:
    raise RuntimeError('DIRECT_URL or DATABASE_URL must be set for migrations')

# Alembic doesn't accept asyncpg scheme; if +asyncpg is present, remove it
if DB_URL.startswith('postgresql+asyncpg://'):
    SA_DB_URL = DB_URL.replace('+asyncpg', '')
else:
    SA_DB_URL = DB_URL

# Set sqlalchemy url for alembic
config.set_main_option('sqlalchemy.url', SA_DB_URL)

# Import project metadata
# Avoid importing the module that enforces env vars at module-import time, so import models only
from database import Base
from models import *  # noqa: F401,F403

# this is the MetaData object for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
