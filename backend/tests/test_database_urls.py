from backend.app.core.database import get_async_database_url, get_sync_database_url


def test_get_sync_database_url_forces_psycopg2_for_postgres():
    assert get_sync_database_url("postgresql+asyncpg://user:pass@postgres:5432/ayurvoice") == (
        "postgresql+psycopg2://user:pass@postgres:5432/ayurvoice"
    )
    assert get_sync_database_url("postgresql://user:pass@postgres:5432/ayurvoice") == (
        "postgresql+psycopg2://user:pass@postgres:5432/ayurvoice"
    )
    assert get_sync_database_url("postgres://user:pass@postgres:5432/ayurvoice") == (
        "postgresql+psycopg2://user:pass@postgres:5432/ayurvoice"
    )
    assert get_sync_database_url("postgresql+psycopg://user:pass@postgres:5432/ayurvoice") == (
        "postgresql+psycopg2://user:pass@postgres:5432/ayurvoice"
    )
    assert get_sync_database_url("sqlite+aiosqlite:///./ayurvoice.db") == "sqlite:///./ayurvoice.db"


def test_get_async_database_url_normalizes_schemes():
    assert get_async_database_url("postgresql://user:pass@postgres:5432/ayurvoice") == (
        "postgresql+asyncpg://user:pass@postgres:5432/ayurvoice"
    )
    assert get_async_database_url("postgres://user:pass@postgres:5432/ayurvoice") == (
        "postgresql+asyncpg://user:pass@postgres:5432/ayurvoice"
    )
    assert get_async_database_url("sqlite:///./ayurvoice.db") == "sqlite+aiosqlite:///./ayurvoice.db"

