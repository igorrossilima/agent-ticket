import asyncio
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from Api.main import app
from Auth.service import gerar_hash_senha
from Auth.token_service import TokenService
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


def criar_auth_headers(session, *, role="admin"):
    sufixo = uuid4().hex
    user = UserRepository(session).criar(
        name=f"Usuario {role}",
        email=f"auth-{role}-{sufixo}@example.com",
        password_hash=gerar_hash_senha("senha-admin-123"),
        role=role,
    )
    token = TokenService().criar_access_token(user)
    return {"Authorization": f"Bearer {token}"}


def test_auth_register_login_e_me(db_session):
    sufixo = uuid4().hex
    email = f"auth-{sufixo}@example.com"
    auth_headers = criar_auth_headers(db_session, role="admin")

    resposta_register = chamar_api(
        "POST",
        "/auth/register",
        headers=auth_headers,
        json={
            "name": "  Usuario Auth  ",
            "email": f"  {email.upper()}  ",
            "password": "senha-segura-123",
            "role": "customer_success",
        },
    )

    assert resposta_register.status_code == 201
    body_register = resposta_register.json()
    assert body_register["email"] == email
    assert body_register["role"] == "customer_success"
    assert "access_token" not in body_register

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
    auth_headers = criar_auth_headers(db_session, role="admin")
    UserRepository(db_session).criar(
        name="Usuario Existente",
        email=email,
        password_hash=gerar_hash_senha("senha-existente-123"),
    )

    resposta = chamar_api(
        "POST",
        "/auth/register",
        headers=auth_headers,
        json={
            "name": "Novo Usuario",
            "email": email,
            "password": "senha-nova-123",
        },
    )

    assert resposta.status_code == 409
    assert "E-mail" in resposta.json()["detail"]


def test_auth_register_exige_admin(db_session):
    resposta_sem_token = chamar_api(
        "POST",
        "/auth/register",
        json={
            "name": "Sem Token",
            "email": f"sem-token-{uuid4().hex}@example.com",
            "password": "senha-nova-123",
        },
    )
    resposta_agent = chamar_api(
        "POST",
        "/auth/register",
        headers=criar_auth_headers(db_session, role="agent"),
        json={
            "name": "Sem Permissao",
            "email": f"sem-permissao-{uuid4().hex}@example.com",
            "password": "senha-nova-123",
        },
    )

    assert resposta_sem_token.status_code == 401
    assert resposta_agent.status_code == 403


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
