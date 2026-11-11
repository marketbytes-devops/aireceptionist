from sqlalchemy import create_engine, inspect, text

from backend.app.core.database import get_async_database_url, get_sync_database_url
from backend.app.core.migrations import INITIAL_REVISION, run_migrations
from backend.app.models.base import Base
import backend.app.models  # noqa: F401


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


def test_run_migrations_handles_existing_legacy_schema_without_knowledge_base(tmp_path):
    db_file = tmp_path / "legacy.db"
    db_url = f"sqlite:///{db_file}"
    engine = create_engine(db_url)
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE clinics ("
                "id VARCHAR(36) PRIMARY KEY, name VARCHAR(255) NOT NULL, "
                "slug VARCHAR(100) NOT NULL, phone_number VARCHAR(50) NOT NULL, "
                "address TEXT, timezone VARCHAR(50) NOT NULL, "
                "created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL)"
            )
        )
    engine.dispose()

    run_migrations(db_url=db_url)

    verify_engine = create_engine(db_url)
    try:
        cols = {c["name"] for c in inspect(verify_engine).get_columns("clinics")}
        assert "knowledge_base" in cols
        with verify_engine.connect() as conn:
            ver = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        assert ver == "b1c2d3e4f5a6"
    finally:
        verify_engine.dispose()


def test_run_migrations_handles_existing_create_all_schema(tmp_path):
    db_file = tmp_path / "create_all.db"
    db_url = f"sqlite:///{db_file}"
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    engine.dispose()

    run_migrations(db_url=db_url)

    verify_engine = create_engine(db_url)
    try:
        cols = {c["name"] for c in inspect(verify_engine).get_columns("clinics")}
        assert "knowledge_base" in cols
        with verify_engine.connect() as conn:
            ver = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        assert ver == "b1c2d3e4f5a6"
    finally:
        verify_engine.dispose()


def test_run_migrations_on_empty_database(tmp_path):
    db_file = tmp_path / "fresh.db"
    db_url = f"sqlite:///{db_file}"

    run_migrations(db_url=db_url)

    verify_engine = create_engine(db_url)
    try:
        tables = set(inspect(verify_engine).get_table_names())
        assert {"clinics", "doctors", "appointments", "call_logs", "alembic_version"}.issubset(tables)
        cols = {c["name"] for c in inspect(verify_engine).get_columns("clinics")}
        assert "knowledge_base" in cols
        with verify_engine.connect() as conn:
            ver = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        assert ver == "b1c2d3e4f5a6"
        assert INITIAL_REVISION == "879c0c11e9a3"
    finally:
        verify_engine.dispose()

