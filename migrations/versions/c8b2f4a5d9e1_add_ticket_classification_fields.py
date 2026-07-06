"""add ticket classification fields

Revision ID: c8b2f4a5d9e1
Revises: b01f15e114d5
Create Date: 2026-07-06 10:48:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c8b2f4a5d9e1"
down_revision: Union[str, Sequence[str], None] = "b01f15e114d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tickets",
        sa.Column("category", sa.String(length=50), server_default="outros", nullable=False),
    )
    op.add_column("tickets", sa.Column("intent", sa.String(length=100), nullable=True))
    op.add_column("tickets", sa.Column("classification_confidence", sa.Float(), nullable=True))
    op.add_column("tickets", sa.Column("classification_reason", sa.Text(), nullable=True))
    op.add_column(
        "tickets",
        sa.Column("requires_human", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.create_index(op.f("ix_tickets_category"), "tickets", ["category"], unique=False)
    op.create_index(op.f("ix_tickets_intent"), "tickets", ["intent"], unique=False)
    op.create_index(op.f("ix_tickets_requires_human"), "tickets", ["requires_human"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tickets_requires_human"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_intent"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_category"), table_name="tickets")
    op.drop_column("tickets", "requires_human")
    op.drop_column("tickets", "classification_reason")
    op.drop_column("tickets", "classification_confidence")
    op.drop_column("tickets", "intent")
    op.drop_column("tickets", "category")
