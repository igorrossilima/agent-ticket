import asyncio
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from Api.main import app
from Auth.service import gerar_hash_senha
from Postgres.config import obter_config_postgres
from Postgres.session import obter_sessao_db
from Users.repository import UserRepository


@pytest.fixture
def db_session():
    engine = create_engine(obter_config_postgres().database_url, pool_pre_ping=True)
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection, autoflush=False, autocommit=False, expire_on_commit=False)
    session = SessionLocal()
    nested = connection.begin_nested()
    overrides_anteriores = dict(app.dependency_overrides)

    @event.listens_for(session, "after_transaction_end")
    def reiniciar_savepoint(session, transaction):
        nonlocal nested

        if not nested.is_active:
            nested = connection.begin_nested()

    def sobrescrever_sessao_db():
        yield session

    app.dependency_overrides[obter_sessao_db] = sobrescrever_sessao_db

    try:
        yield session
    finally:
        app.dependency_overrides = overrides_anteriores
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


def chamar_api(method, path, json=None, headers=None):
    async def executar():
        transport = httpx.ASGITransport(
            app=app,
            raise_app_exceptions=False,
        )
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.request(method, path, json=json, headers=headers)

    return asyncio.run(executar())


def test_auth_register_login_e_me(db_session):
    sufixo = uuid4().hex
    email = f"auth-{sufixo}@example.com"

    resposta_register = chamar_api(
        "POST",
        "/auth/register",
        json={
            "name": "  Usuario Auth  ",
            "email": f"  {email.upper()}  ",
            "password": "senha-segura-123",
            "role": "customer_success",
        },
    )

    assert resposta_register.status_code == 201
    body_register = resposta_register.json()
    assert body_register["token_type"] == "bearer"
    assert body_register["access_token"]
    assert body_register["user"]["email"] == email
    assert body_register["user"]["role"] == "customer_success"

    resposta_login = chamar_api(
        "POST",
        "/auth/login",
        json={
            "email": email,
            "password": "senha-segura-123",
        },
    )

    assert resposta_login.status_code == 200
    assert resposta_login.json()["access_token"]
    assert resposta_login.json()["user"]["email"] == email

    resposta_me = chamar_api(
        "GET",
        "/auth/me",
        headers={"Authorization": f"Bearer {resposta_login.json()['access_token']}"},
    )

    assert resposta_me.status_code == 200
    assert resposta_me.json()["email"] == email


def test_auth_register_rejeita_email_duplicado(db_session):
    sufixo = uuid4().hex
    email = f"duplicado-{sufixo}@example.com"
    UserRepository(db_session).criar(
        name="Usuario Existente",
        email=email,
        password_hash=gerar_hash_senha("senha-existente-123"),
    )

    resposta = chamar_api(
        "POST",
        "/auth/register",
        json={
            "name": "Novo Usuario",
            "email": email,
            "password": "senha-nova-123",
        },
    )

    assert resposta.status_code == 409
    assert "E-mail" in resposta.json()["detail"]


def test_auth_login_rejeita_credenciais_invalidas(db_session):
    sufixo = uuid4().hex
    email = f"login-invalido-{sufixo}@example.com"
    UserRepository(db_session).criar(
        name="Usuario Login",
        email=email,
        password_hash=gerar_hash_senha("senha-correta-123"),
    )

    resposta = chamar_api(
        "POST",
        "/auth/login",
        json={
            "email": email,
            "password": "senha-errada",
        },
    )

    assert resposta.status_code == 401
    assert "senha" in resposta.json()["detail"]


def test_auth_me_rejeita_token_invalido(db_session):
    resposta = chamar_api(
        "GET",
        "/auth/me",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert resposta.status_code == 401
