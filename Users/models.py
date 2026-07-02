from __future__ import annotations

from datetime import datetime
from uuid import UUID as PythonUUID
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Postgres.base import Base
from Shared.constants import USER_ROLES


class User(Base):
    __tablename__ = "users"

    id: Mapped[PythonUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default=USER_ROLES[1], server_default=USER_ROLES[1])
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    assigned_tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        back_populates="assigned_user",
        foreign_keys="Ticket.assigned_user_id",
    )
    messages: Mapped[list["TicketMessage"]] = relationship(
        "TicketMessage",
        back_populates="sender_user",
        foreign_keys="TicketMessage.sender_user_id",
    )
