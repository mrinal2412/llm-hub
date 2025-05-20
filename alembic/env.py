import os
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from dotenv import load_dotenv

# 1) Load environment variables so DATABASE_URL is set
load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]

# this is the Alembic Config object
config = context.config

# 2) Override the URL in alembic.ini
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging.
if config.config_file_name:
    fileConfig(config.config_file_name)

# 3) Import your MetaData
#    Adjust the import path to match your project structure
from backend.flask.model.models import Base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode: emit SQL to the script output."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode: connect to the DB and run them."""
    connectable: AsyncEngine = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    # use an async connection, then run the sync migration functions:
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def do_run_migrations(connection):
    """Callback invoked by run_sync; runs the migrations on a sync connection."""
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        # **OPTIONAL**: You can pass other flags here, e.g. 
        # compare_type=True, compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Kick off the async online runner
    asyncio.run(run_migrations_online())
