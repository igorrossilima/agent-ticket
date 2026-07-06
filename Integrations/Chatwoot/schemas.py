from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from Shared.constants import TICKET_CHANNELS


class ChatwootMessageRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str = Field(min_length=1, max_length=120)
    message_id: str | None = Field(default=None, max_length=120)
    contact_id: str | None = Field(default=None, max_length=120)
    contact_name: str | None = Field(default=None, max_length=255)
    contact_email: str | None = Field(default=None, max_length=320)
    contact_phone: str | None = Field(default=None, max_length=30)
    channel: str = "chatwoot"
    top_k: int = Field(default=3, ge=1, le=10)
    provedor_ia: str = "openai"
    force_new_ticket: bool = False

    @field_validator("message", "conversation_id", "channel", "provedor_ia")
    @classmethod
    def limpar_texto_obrigatorio(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Campo obrigatorio nao pode ser vazio.")
        return value

    @field_validator("message_id", "contact_id", "contact_name", "contact_email", "contact_phone")
    @classmethod
    def limpar_texto(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None

    @field_validator("contact_email")
    @classmethod
    def normalizar_email(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return value.strip().lower() or None

    @field_validator("channel")
    @classmethod
    def validar_channel(cls, value: str) -> str:
        value = value.strip()
        if value not in TICKET_CHANNELS:
            raise ValueError(f"Canal invalido: {value}.")
        return value


class ChatwootMessageResponse(BaseModel):
    resposta: str
    ticket_id: UUID
    customer_id: UUID
    created_new_ticket: bool
    status: str
    category: str
    intent: str | None
    requires_human: bool
    should_reply: bool = True
