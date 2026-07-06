from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from Shared.constants import (
    DEFAULT_TICKET_CATEGORY,
    DEFAULT_TICKET_CHANNEL,
    DEFAULT_TICKET_PRIORITY,
    DEFAULT_TICKET_SOURCE,
    MESSAGE_SENDER_TYPES,
    TICKET_CATEGORIES,
    TICKET_CHANNELS,
    TICKET_PRIORITIES,
    TICKET_SOURCES,
    TICKET_STATUSES,
)


class TicketCreate(BaseModel):
    customer_id: UUID
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    assigned_user_id: UUID | None = None
    priority: str = DEFAULT_TICKET_PRIORITY
    source: str = DEFAULT_TICKET_SOURCE
    channel: str = DEFAULT_TICKET_CHANNEL
    external_conversation_id: str | None = Field(default=None, max_length=120)
    category: str = DEFAULT_TICKET_CATEGORY
    intent: str | None = None
    classification_confidence: float | None = Field(default=None, ge=0, le=1)
    classification_reason: str | None = None
    requires_human: bool = False
    ai_summary: str | None = None

    @field_validator("title")
    @classmethod
    def validar_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("O titulo do ticket nao pode ser vazio.")
        return value

    @field_validator("description", "external_conversation_id", "intent", "classification_reason", "ai_summary")
    @classmethod
    def limpar_texto_opcional(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None

    @field_validator("priority")
    @classmethod
    def validar_priority(cls, value: str) -> str:
        value = value.strip()
        if value not in TICKET_PRIORITIES:
            raise ValueError(f"Prioridade invalida: {value}.")
        return value

    @field_validator("source")
    @classmethod
    def validar_source(cls, value: str) -> str:
        value = value.strip()
        if value not in TICKET_SOURCES:
            raise ValueError(f"Origem invalida: {value}.")
        return value

    @field_validator("channel")
    @classmethod
    def validar_channel(cls, value: str) -> str:
        value = value.strip()
        if value not in TICKET_CHANNELS:
            raise ValueError(f"Canal invalido: {value}.")
        return value

    @field_validator("category")
    @classmethod
    def validar_category(cls, value: str) -> str:
        value = value.strip()
        if value not in TICKET_CATEGORIES:
            raise ValueError(f"Categoria invalida: {value}.")
        return value


class TicketClassificationUpdate(BaseModel):
    category: str = DEFAULT_TICKET_CATEGORY
    intent: str | None = None
    classification_confidence: float | None = Field(default=None, ge=0, le=1)
    classification_reason: str | None = None
    requires_human: bool = False

    @field_validator("category")
    @classmethod
    def validar_category(cls, value: str) -> str:
        value = value.strip()
        if value not in TICKET_CATEGORIES:
            raise ValueError(f"Categoria invalida: {value}.")
        return value

    @field_validator("intent", "classification_reason")
    @classmethod
    def limpar_texto_opcional(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class TicketStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validar_status(cls, value: str) -> str:
        value = value.strip()
        if value not in TICKET_STATUSES:
            raise ValueError(f"Status invalido: {value}.")
        return value


class TicketAssignmentUpdate(BaseModel):
    assigned_user_id: UUID | None


class TicketMessageCreate(BaseModel):
    ticket_id: UUID
    sender_type: str
    body: str = Field(min_length=1)
    sender_user_id: UUID | None = None
    sender_customer_id: UUID | None = None
    external_message_id: str | None = Field(default=None, max_length=120)
    metadata: dict[str, Any] | None = None

    @field_validator("sender_type")
    @classmethod
    def validar_sender_type(cls, value: str) -> str:
        value = value.strip()
        if value not in MESSAGE_SENDER_TYPES:
            raise ValueError(f"Tipo de remetente invalido: {value}.")
        return value

    @field_validator("body")
    @classmethod
    def validar_body(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("A mensagem nao pode ser vazia.")
        return value

    @field_validator("external_message_id")
    @classmethod
    def limpar_external_message_id(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class TicketMessageCreateRequest(BaseModel):
    sender_type: str
    body: str = Field(min_length=1)
    sender_user_id: UUID | None = None
    sender_customer_id: UUID | None = None
    external_message_id: str | None = Field(default=None, max_length=120)
    metadata: dict[str, Any] | None = None

    @field_validator("sender_type")
    @classmethod
    def validar_sender_type(cls, value: str) -> str:
        value = value.strip()
        if value not in MESSAGE_SENDER_TYPES:
            raise ValueError(f"Tipo de remetente invalido: {value}.")
        return value

    @field_validator("body")
    @classmethod
    def validar_body(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("A mensagem nao pode ser vazia.")
        return value

    @field_validator("external_message_id")
    @classmethod
    def limpar_external_message_id(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class TicketMessageRead(BaseModel):
    id: UUID
    ticket_id: UUID
    sender_type: str
    sender_user_id: UUID | None
    sender_customer_id: UUID | None
    external_message_id: str | None
    body: str
    metadata: dict[str, Any] | None = Field(default=None, validation_alias="metadata_")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TicketRead(BaseModel):
    id: UUID
    customer_id: UUID
    assigned_user_id: UUID | None
    title: str
    description: str | None
    status: str
    priority: str
    source: str
    channel: str
    external_conversation_id: str | None
    category: str
    intent: str | None
    classification_confidence: float | None
    classification_reason: str | None
    requires_human: bool
    ai_summary: str | None
    last_message_at: datetime | None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class TicketDetailRead(TicketRead):
    messages: list[TicketMessageRead] = Field(default_factory=list)
