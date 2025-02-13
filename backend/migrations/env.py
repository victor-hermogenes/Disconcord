import os
import sys
from sqlalchemy import engine_from_config, pool
from alembic import context

from backend.app.database import DATA_BASE_SYNC, Base

config = context.config
config.set_main_option("sqlalchemy.url", DATA_BASE_SYNC)

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(url=DATA_BASE_SYNC, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
