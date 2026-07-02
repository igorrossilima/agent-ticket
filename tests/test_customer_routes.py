import asyncio
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from Api.main import app
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
    app.state.auth_headers = criar_auth_headers(session)

    try:
        yield session
    finally:
        app.dependency_overrides = overrides_anteriores
        if hasattr(app.state, "auth_headers"):
            delattr(app.state, "auth_headers")
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


def chamar_api(method, path, json=None, headers=None):
    headers = app.state.auth_headers if headers is None else headers

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


def criar_auth_headers(session):
    sufixo = uuid4().hex
    user = UserRepository(session).criar(
        name="Usuario Auth Customers",
        email=f"auth-customers-{sufixo}@example.com",
        password_hash="hash-teste",
        role="admin",
    )
    token = TokenService().criar_access_token(user)
    return {"Authorization": f"Bearer {token}"}


def test_customer_routes_criam_listam_e_buscam_customer(db_session):
    sufixo = uuid4().hex
    email = f"cliente-{sufixo}@example.com"
    document = f"doc-{sufixo[:12]}"

    resposta_criacao = chamar_api(
        "POST",
        "/customers",
        json={
            "name": "  Cliente API  ",
            "email": f"  {email}  ",
            "phone": "  +5511999999999  ",
            "document": f"  {document}  ",
        },
    )

    assert resposta_criacao.status_code == 201
    customer = resposta_criacao.json()
    assert customer["name"] == "Cliente API"
    assert customer["email"] == email
    assert customer["phone"] == "+5511999999999"
    assert customer["document"] == document

    resposta_listagem = chamar_api("GET", "/customers")
    resposta_por_id = chamar_api("GET", f"/customers/{customer['id']}")
    resposta_por_email = chamar_api("GET", f"/customers/by-email/{email}")
    resposta_por_documento = chamar_api("GET", f"/customers/by-document/{document}")

    assert resposta_listagem.status_code == 200
    assert customer["id"] in [item["id"] for item in resposta_listagem.json()]
    assert resposta_por_id.status_code == 200
    assert resposta_por_id.json()["id"] == customer["id"]
    assert resposta_por_email.status_code == 200
    assert resposta_por_email.json()["id"] == customer["id"]
    assert resposta_por_documento.status_code == 200
    assert resposta_por_documento.json()["id"] == customer["id"]


def test_customer_routes_atualizam_customer(db_session):
    sufixo = uuid4().hex
    resposta_criacao = chamar_api(
        "POST",
        "/customers",
        json={
            "name": "Cliente Antigo",
            "email": f"cliente-antigo-{sufixo}@example.com",
        },
    )
    customer = resposta_criacao.json()

    resposta_atualizacao = chamar_api(
        "PATCH",
        f"/customers/{customer['id']}",
        json={
            "name": "  Cliente Atualizado  ",
            "phone": "  +5511888888888  ",
            "document": None,
        },
    )

    assert resposta_atualizacao.status_code == 200
    assert resposta_atualizacao.json()["name"] == "Cliente Atualizado"
    assert resposta_atualizacao.json()["email"] == customer["email"]
    assert resposta_atualizacao.json()["phone"] == "+5511888888888"
    assert resposta_atualizacao.json()["document"] is None


def test_customer_routes_exigem_autenticacao(db_session):
    resposta = chamar_api(
        "GET",
        "/customers",
        headers={},
    )

    assert resposta.status_code == 401


def test_customer_routes_retornam_404_para_customer_inexistente(db_session):
    resposta = chamar_api("GET", f"/customers/{uuid4()}")

    assert resposta.status_code == 404
    assert "Cliente" in resposta.json()["detail"]
