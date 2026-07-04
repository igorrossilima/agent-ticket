from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from Postgres.config import obter_config_postgres


engine = create_engine(
    obter_config_postgres().database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def obter_sessao_db() -> Generator[Session, None, None]:
    sessao = SessionLocal()

    try:
        yield sessao
    finally:
        sessao.close()
