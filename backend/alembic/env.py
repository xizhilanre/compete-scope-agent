"""Alembic async environment — used by `alembic revision --autogenerate`."""

import asyncio

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

# Import all models so DeclarativeBase.metadata is populated
import backend.db.models  # noqa: F401
from backend.config import settings
from backend.db.database import Base

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Generate SQL script without connecting to the database."""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Connect to the live database and run migrations."""
    connectable = create_async_engine(settings.DATABASE_URL)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
