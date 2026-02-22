import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic import context
from app.config import settings
from app.models import *  # 모든 모델 import
from sqlmodel import SQLModel

target_metadata = SQLModel.metadata

config = context.config


def run_migrations_offline():
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    from sqlalchemy import create_engine
    connectable = create_engine(settings.DATABASE_URL)

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
