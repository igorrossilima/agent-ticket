from __future__ import annotations

from datetime import datetime
from uuid import UUID as PythonUUID
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Postgres.base import Base
from Shared.constants import (
    DEFAULT_TICKET_PRIORITY,
    DEFAULT_TICKET_SOURCE,
    DEFAULT_TICKET_STATUS,
)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[PythonUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    customer_id: Mapped[PythonUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )
    assigned_user_id: Mapped[PythonUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=DEFAULT_TICKET_STATUS,
        server_default=DEFAULT_TICKET_STATUS,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=DEFAULT_TICKET_PRIORITY,
        server_default=DEFAULT_TICKET_PRIORITY,
    )
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=DEFAULT_TICKET_SOURCE,
        server_default=DEFAULT_TICKET_SOURCE,
    )
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="tickets",
    )
    assigned_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="assigned_tickets",
        foreign_keys=[assigned_user_id],
    )
    messages: Mapped[list["TicketMessage"]] = relationship(
        "TicketMessage",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_tickets_status_last_message_at", "status", "last_message_at"),
    )


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id: Mapped[PythonUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    ticket_id: Mapped[PythonUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_type: Mapped[str] = mapped_column(String(50), nullable=False)
    sender_user_id: Mapped[PythonUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    sender_customer_id: Mapped[PythonUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=True,
        index=True,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    ticket: Mapped["Ticket"] = relationship(
        "Ticket",
        back_populates="messages",
    )
    sender_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="messages",
        foreign_keys=[sender_user_id],
    )
    sender_customer: Mapped["Customer | None"] = relationship(
        "Customer",
        back_populates="messages",
        foreign_keys=[sender_customer_id],
    )
