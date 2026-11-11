from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.app.core.config import settings
from backend.app.models.base import Base

_POSTGRES_PREFIXES = (
    "postgres://",
    "postgresql+asyncpg://",
    "postgresql+psycopg://",
    "postgresql+psycopg2://",
    "postgresql://",
)


def get_async_database_url(db_url: str) -> str:
    """Ensure a database URL uses the async driver configured for runtime."""
    if db_url.startswith("postgres://"):
        return db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    if db_url.startswith("postgresql://"):
        return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return db_url


def get_sync_database_url(db_url: str) -> str:
    """Convert any async or generic database URL to an explicit sync driver URL for Alembic."""
    if "+aiosqlite" in db_url:
        return db_url.replace("+aiosqlite", "")
    for prefix in _POSTGRES_PREFIXES:
        if db_url.startswith(prefix):
            return db_url.replace(prefix, "postgresql+psycopg2://", 1)
    return db_url


# Format connection string if needed for async drivers
database_url = get_async_database_url(settings.DATABASE_URL)

# SQLite requires specific connect args for foreign key constraints and async multithreading
connect_args = {}
if "sqlite" in database_url:
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

