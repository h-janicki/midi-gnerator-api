from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def build_postgres_url(
    user: str,
    password: str,
    host: str,
    port: int | str,
    name: str,
    driver: str = "postgresql+asyncpg",
) -> str:
    return f"{driver}://{user}:{password}@{host}:{port}/{name}"


def make_engine(url: str, *, echo: bool = False, pool_pre_ping: bool = True) -> AsyncEngine:
    return create_async_engine(url, echo=echo, pool_pre_ping=pool_pre_ping)


def make_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def make_get_db(session_factory: async_sessionmaker[AsyncSession]):
    async def get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session
    return get_db
