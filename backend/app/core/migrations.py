"""Idempotent Alembic migration runner that stamps pre-Alembic schemas cleanly."""

from pathlib import Path
from typing import Optional

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from backend.app.core.config import settings
from backend.app.core.database import get_sync_database_url

INITIAL_REVISION = "879c0c11e9a3"
DEFAULT_ALEMBIC_INI = str(Path(__file__).resolve().parents[2] / "alembic.ini")


def _has_alembic_revision(sync_engine) -> bool:
    inspector = inspect(sync_engine)
    if not inspector.has_table("alembic_version"):
        return False
    with sync_engine.connect() as conn:
        row = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).first()
    return row is not None


def run_migrations(
    alembic_ini_path: str = DEFAULT_ALEMBIC_INI,
    db_url: Optional[str] = None,
) -> None:
    """Stamp an existing pre-Alembic database at initial_schema, then upgrade to head."""
    sync_url = get_sync_database_url(db_url or settings.DATABASE_URL)
    cfg = Config(alembic_ini_path)
    cfg.attributes["db_url"] = sync_url

    engine = create_engine(sync_url)
    try:
        inspector = inspect(engine)
        if inspector.has_table("clinics") and not _has_alembic_revision(engine):
            command.stamp(cfg, INITIAL_REVISION)
    finally:
        engine.dispose()

    command.upgrade(cfg, "head")


if __name__ == "__main__":
    run_migrations()

