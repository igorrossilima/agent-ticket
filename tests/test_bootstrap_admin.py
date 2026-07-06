from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Auth.bootstrap_admin import BootstrapAdminError, criar_primeiro_admin
from Auth.service import gerar_hash_senha
from Postgres.config import obter_config_postgres
from Users.repository import UserRepository


def criar_sessao_teste():
    engine = create_engine(obter_config_postgres().database_url, pool_pre_ping=True)
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection, autoflush=False, autocommit=False, expire_on_commit=False)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


def test_bootstrap_admin_valida_campos_obrigatorios():
    with pytest.raises(BootstrapAdminError):
        criar_primeiro_admin(
            session=None,
            name="",
            email="admin@example.com",
            password="senha-admin-123",
        )


def test_bootstrap_admin_rejeita_quando_ja_existe_usuario():
    session_generator = criar_sessao_teste()
    session = next(session_generator)

    try:
        UserRepository(session).criar(
            name="Usuario Existente",
            email=f"existente-{uuid4().hex}@example.com",
            password_hash=gerar_hash_senha("senha-existente-123"),
            role="admin",
        )

        with pytest.raises(BootstrapAdminError):
            criar_primeiro_admin(
                session=session,
                name="Primeiro Admin",
                email=f"primeiro-admin-{uuid4().hex}@example.com",
                password="senha-admin-123",
            )
    finally:
        next(session_generator, None)
