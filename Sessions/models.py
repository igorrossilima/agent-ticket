from datetime import datetime, timezone

from pydantic import BaseModel, Field


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)

# passo 11
class SessaoConversa(BaseModel):
    session_id: str = Field(min_length=1)
    usuario_id: str = Field(min_length=1)
    ativa: bool = True
    criada_em: datetime = Field(default_factory=agora_utc)
    atualizada_em: datetime = Field(default_factory=agora_utc)
