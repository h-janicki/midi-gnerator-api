"""create generations table

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-21 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "generations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("track_type", sa.String(length=20), nullable=False),
        sa.Column("key", sa.String(length=20), nullable=False),
        sa.Column("bpm", sa.Integer(), nullable=False),
        sa.Column("bars", sa.Integer(), nullable=False),
        sa.Column("note_count", sa.Integer(), nullable=False),
        sa.Column("s3_key", sa.String(length=255), nullable=False, unique=True),
        sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_generations_created_at", "generations", ["created_at"])
    op.create_index("ix_generations_is_favorite", "generations", ["is_favorite"])


def downgrade() -> None:
    op.drop_index("ix_generations_is_favorite", table_name="generations")
    op.drop_index("ix_generations_created_at", table_name="generations")
    op.drop_table("generations")
