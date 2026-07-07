from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    mensagem: str
    customer_id: UUID
    ticket_id: UUID | None = None
    title: str | None = Field(default=None, max_length=255)
    top_k: int = Field(default=3, ge=1, le=10)


class ChatResponse(BaseModel):
    resposta: str
    ticket_id: UUID
    top_k: int
    provedor_ia: str
