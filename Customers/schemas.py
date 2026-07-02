from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=30)
    document: str | None = Field(default=None, max_length=30)

    @field_validator("name")
    @classmethod
    def validar_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("O nome do cliente nao pode ser vazio.")
        return value

    @field_validator("email", "phone", "document")
    @classmethod
    def limpar_texto_opcional(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=30)
    document: str | None = Field(default=None, max_length=30)

    @field_validator("name")
    @classmethod
    def validar_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        if not value:
            raise ValueError("O nome do cliente nao pode ser vazio.")
        return value

    @field_validator("email", "phone", "document")
    @classmethod
    def limpar_texto_opcional(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class CustomerRead(BaseModel):
    id: UUID
    name: str
    email: str | None
    phone: str | None
    document: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
