from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/agent_ticket"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def obter_config_postgres() -> PostgresSettings:
    return PostgresSettings()
