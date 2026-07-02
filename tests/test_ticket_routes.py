import asyncio
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from Api.main import app
from Auth.token_service import TokenService
from Customers.repository import CustomerRepository
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
        name="Usuario Auth Tickets",
        email=f"auth-tickets-{sufixo}@example.com",
        password_hash="hash-teste",
        role="admin",
    )
    token = TokenService().criar_access_token(user)
    return {"Authorization": f"Bearer {token}"}


def criar_customer_e_user(session):
    sufixo = uuid4().hex
    customer = CustomerRepository(session).criar(
        name="Cliente API",
        email=f"cliente-api-{sufixo}@example.com",
    )
    user = UserRepository(session).criar(
        name="Agente API",
        email=f"agente-api-{sufixo}@example.com",
        password_hash="hash-teste",
    )
    return customer, user


def test_ticket_routes_criam_listam_e_detalham_ticket(db_session):
    customer, user = criar_customer_e_user(db_session)

    resposta_criacao = chamar_api(
        "POST",
        "/tickets",
        json={
            "customer_id": str(customer.id),
            "assigned_user_id": str(user.id),
            "title": "  Falha no login  ",
            "description": "  Cliente nao consegue acessar.  ",
            "source": "api",
        },
    )

    assert resposta_criacao.status_code == 201
    ticket = resposta_criacao.json()
    assert ticket["title"] == "Falha no login"
    assert ticket["description"] == "Cliente nao consegue acessar."
    assert ticket["status"] == "open"
    assert ticket["priority"] == "medium"

    resposta_listagem = chamar_api("GET", "/tickets?status=open")
    resposta_detalhe = chamar_api("GET", f"/tickets/{ticket['id']}")

    assert resposta_listagem.status_code == 200
    assert [item["id"] for item in resposta_listagem.json()] == [ticket["id"]]
    assert resposta_detalhe.status_code == 200
    assert resposta_detalhe.json()["messages"] == []


def test_ticket_routes_adicionam_mensagem_e_atualizam_status(db_session):
    customer, _ = criar_customer_e_user(db_session)
    resposta_criacao = chamar_api(
        "POST",
        "/tickets",
        json={
            "customer_id": str(customer.id),
            "title": "Problema com acesso",
        },
    )
    ticket = resposta_criacao.json()

    resposta_mensagem_cliente = chamar_api(
        "POST",
        f"/tickets/{ticket['id']}/messages",
        json={
            "sender_type": "customer",
            "sender_customer_id": str(customer.id),
            "body": "  Ainda nao consigo acessar.  ",
        },
    )
    resposta_detalhe_cliente = chamar_api("GET", f"/tickets/{ticket['id']}")

    assert resposta_mensagem_cliente.status_code == 201
    assert resposta_mensagem_cliente.json()["body"] == "Ainda nao consigo acessar."
    assert resposta_detalhe_cliente.json()["status"] == "in_progress"

    resposta_mensagem_ia = chamar_api(
        "POST",
        f"/tickets/{ticket['id']}/messages",
        json={
            "sender_type": "ai_agent",
            "body": "Tente redefinir sua senha.",
            "metadata": {"confidence": 0.9, "rag_sources": ["faq-login"]},
        },
    )
    resposta_detalhe_ia = chamar_api("GET", f"/tickets/{ticket['id']}")

    assert resposta_mensagem_ia.status_code == 201
    assert resposta_mensagem_ia.json()["metadata"]["rag_sources"] == ["faq-login"]
    assert resposta_detalhe_ia.json()["status"] == "pending"
    assert len(resposta_detalhe_ia.json()["messages"]) == 2


def test_ticket_routes_atualizam_status_e_atribuicao(db_session):
    customer, user = criar_customer_e_user(db_session)
    resposta_criacao = chamar_api(
        "POST",
        "/tickets",
        json={
            "customer_id": str(customer.id),
            "title": "Revisar cobranca",
        },
    )
    ticket = resposta_criacao.json()

    resposta_atribuicao = chamar_api(
        "PATCH",
        f"/tickets/{ticket['id']}/assignment",
        json={"assigned_user_id": str(user.id)},
    )
    resposta_status = chamar_api(
        "PATCH",
        f"/tickets/{ticket['id']}/status",
        json={"status": "closed"},
    )

    assert resposta_atribuicao.status_code == 200
    assert resposta_atribuicao.json()["assigned_user_id"] == str(user.id)
    assert resposta_status.status_code == 200
    assert resposta_status.json()["status"] == "closed"
    assert resposta_status.json()["closed_at"] is not None


def test_ticket_routes_exigem_autenticacao(db_session):
    resposta = chamar_api(
        "GET",
        "/tickets",
        headers={},
    )

    assert resposta.status_code == 401


def test_ticket_routes_retornam_404_para_customer_inexistente(db_session):
    resposta = chamar_api(
        "POST",
        "/tickets",
        json={
            "customer_id": str(uuid4()),
            "title": "Cliente inexistente",
        },
    )

    assert resposta.status_code == 404
    assert "Cliente" in resposta.json()["detail"]
