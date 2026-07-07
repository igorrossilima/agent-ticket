from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    ai_provider: str = Field(default="openai", validation_alias="AI_PROVIDER")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @field_validator("ai_provider")
    @classmethod
    def limpar_ai_provider(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("AI_PROVIDER nao pode ser vazio.")
        return value


@lru_cache
def obter_ai_settings() -> AISettings:
    return AISettings()
