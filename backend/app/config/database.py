from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import (
    build_postgres_url,
    make_engine,
    make_session_factory,
)
from app.config.app import settings


database_url = build_postgres_url(
    user=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    name=settings.db_name,
)

engine = make_engine(
    database_url,
    echo=settings.log_level == "DEBUG",
    pool_pre_ping=True,
)

SessionLocal = make_session_factory(engine)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session