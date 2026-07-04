from __future__ import annotations

from datetime import datetime
from uuid import UUID as PythonUUID
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Postgres.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[PythonUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    document: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        back_populates="customer",
    )
    messages: Mapped[list["TicketMessage"]] = relationship(
        "TicketMessage",
        back_populates="sender_customer",
    )
