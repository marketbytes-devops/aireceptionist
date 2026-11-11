"""add_knowledge_base_to_clinics

Revision ID: b1c2d3e4f5a6
Revises: 879c0c11e9a3
Create Date: 2026-11-11 18:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, None] = "879c0c11e9a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_cols = {col["name"] for col in inspector.get_columns("clinics")}
    if "knowledge_base" not in existing_cols:
        op.add_column("clinics", sa.Column("knowledge_base", sa.Text(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_cols = {col["name"] for col in inspector.get_columns("clinics")}
    if "knowledge_base" in existing_cols:
        op.drop_column("clinics", "knowledge_base")

