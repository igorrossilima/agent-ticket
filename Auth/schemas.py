from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from Shared.constants import USER_ROLES


class UserRead(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=8, max_length=72)
    role: str = "agent"

    @field_validator("name", "email", "role")
    @classmethod
    def limpar_texto(cls, value: str) -> str:
        return value.strip()

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("role")
    @classmethod
    def validar_role(cls, value: str) -> str:
        value = value.strip()
        if value not in USER_ROLES:
            raise ValueError(f"Role invalida: {value}.")
        return value


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=1, max_length=72)

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, value: str) -> str:
        return value.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
