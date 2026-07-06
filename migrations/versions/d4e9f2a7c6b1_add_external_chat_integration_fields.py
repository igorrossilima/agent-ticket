"""add external chat integration fields

Revision ID: d4e9f2a7c6b1
Revises: c8b2f4a5d9e1
Create Date: 2026-07-06 17:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4e9f2a7c6b1"
down_revision: Union[str, Sequence[str], None] = "c8b2f4a5d9e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("customers", sa.Column("external_contact_id", sa.String(length=120), nullable=True))
    op.add_column("customers", sa.Column("external_channel", sa.String(length=50), nullable=True))
    op.create_index(op.f("ix_customers_external_contact_id"), "customers", ["external_contact_id"], unique=False)
    op.create_index(op.f("ix_customers_external_channel"), "customers", ["external_channel"], unique=False)

    op.add_column(
        "tickets",
        sa.Column("channel", sa.String(length=50), server_default="platform", nullable=False),
    )
    op.add_column("tickets", sa.Column("external_conversation_id", sa.String(length=120), nullable=True))
    op.create_index(op.f("ix_tickets_channel"), "tickets", ["channel"], unique=False)
    op.create_index(
        op.f("ix_tickets_external_conversation_id"),
        "tickets",
        ["external_conversation_id"],
        unique=False,
    )

    op.add_column("ticket_messages", sa.Column("external_message_id", sa.String(length=120), nullable=True))
    op.create_index(
        op.f("ix_ticket_messages_external_message_id"),
        "ticket_messages",
        ["external_message_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_ticket_messages_external_message_id"), table_name="ticket_messages")
    op.drop_column("ticket_messages", "external_message_id")

    op.drop_index(op.f("ix_tickets_external_conversation_id"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_channel"), table_name="tickets")
    op.drop_column("tickets", "external_conversation_id")
    op.drop_column("tickets", "channel")

    op.drop_index(op.f("ix_customers_external_channel"), table_name="customers")
    op.drop_index(op.f("ix_customers_external_contact_id"), table_name="customers")
    op.drop_column("customers", "external_channel")
    op.drop_column("customers", "external_contact_id")
