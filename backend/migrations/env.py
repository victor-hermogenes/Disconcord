from logging.config import fileConfig
from sqlalchemy import engine_from_config, create_engine, pool
from alembic import context
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

from database import DATA_BASE_SYNC
from models.user import Base as UserBase
from models.room import Base as RoomBase

config = context.config
config.set_main_option("sqlalchemy.url", DATA_BASE_SYNC)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = [UserBase.metadata, RoomBase.metadata]

def run_migrations_offline() -> None:
    """Roda migrações no modo 'offline'. """
    context.configure(
        url=DATA_BASE_SYNC, 
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Roda migrações nmo modo 'online'."""
    connectable = create_engine(DATA_BASE_SYNC, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()