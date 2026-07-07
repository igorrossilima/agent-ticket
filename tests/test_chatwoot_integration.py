import asyncio
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import patch

import httpx
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from Api.main import app
from Integrations.Chatwoot.routes import obter_executor_fluxo
from Postgres.config import obter_config_postgres
from Postgres.session import obter_sessao_db
from RAG.structure import DocumentoRAG
from Tickets.repository import TicketMessageRepository, TicketRepository


class FakeClassifier:
    def __init__(self, provedor_ia="fake"):
        self.provedor_ia = provedor_ia

    def executar(self, mensagem):
        if "cobranca" in mensagem.lower():
            return {
                "categoria": "financeiro",
                "confianca": 0.9,
                "intencao": "revisar_cobranca",
                "justificativa": "Cliente perguntou sobre cobranca.",
                "termos_busca": ["cobranca"],
            }

        return {
            "categoria": "eventos",
            "confianca": 0.92,
            "intencao": "consultar_eventos",
            "justificativa": "Cliente perguntou sobre eventos.",
            "termos_busca": ["eventos"],
        }


class FakeFluxoExecutor:
    def __init__(self):
        self.chamadas = []

    def __call__(self, **kwargs):
        self.chamadas.append(kwargs)
        return SimpleNamespace(
            resposta="Resposta via integracao.",
            classificacao=kwargs["classificacao_inicial"],
            documentos=[
                DocumentoRAG(
                    id="wiki-integracao-1",
                    text="Conteudo usado pela resposta.",
                    metadados={"documento_origem_id": "wiki-integracao"},
                    score=0.89,
                )
            ],
        )


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
    executor = FakeFluxoExecutor()

    async def sobrescrever_executor():
        return executor

    app.dependency_overrides[obter_executor_fluxo] = sobrescrever_executor
    app.state.fake_executor = executor

    try:
        yield session
    finally:
        app.dependency_overrides = overrides_anteriores
        if hasattr(app.state, "fake_executor"):
            delattr(app.state, "fake_executor")
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


def chamar_api(method, path, json=None):
    async def executar():
        transport = httpx.ASGITransport(
            app=app,
            raise_app_exceptions=False,
        )
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.request(method, path, json=json)

    return asyncio.run(executar())


def payload_base(**overrides):
    sufixo = uuid4().hex
    payload = {
        "message": "Como vejo eventos de velocidade?",
        "conversation_id": f"conv-{sufixo}",
        "message_id": f"msg-{sufixo}",
        "contact_id": f"contact-{sufixo}",
        "contact_name": "Cliente Chatwoot",
        "contact_email": f"chatwoot-{sufixo}@example.com",
        "contact_phone": f"+5511{sufixo[:8]}",
        "channel": "chatwoot",
        "top_k": 2,
    }
    payload.update(overrides)
    return payload


def test_chatwoot_cria_customer_ticket_e_rastreia_mensagem(db_session):
    payload = payload_base()

    with patch("Integrations.Chatwoot.service.Classifier", FakeClassifier):
        resposta = chamar_api("POST", "/integrations/chatwoot/messages", json=payload)

    assert resposta.status_code == 200
    body = resposta.json()
    assert body["created_new_ticket"] is True
    assert body["category"] == "eventos"
    assert body["requires_human"] is False

    ticket = TicketRepository(db_session).obter_por_id(body["ticket_id"])
    mensagens = TicketMessageRepository(db_session).listar_por_ticket(ticket.id)

    assert ticket.channel == "chatwoot"
    assert ticket.external_conversation_id == payload["conversation_id"]
    assert ticket.category == "eventos"
    assert mensagens[0].external_message_id == payload["message_id"]
    assert mensagens[0].metadata_["external"]["conversation_id"] == payload["conversation_id"]
    assert mensagens[1].metadata_["rag_docs"][0]["id"] == "wiki-integracao-1"


def test_chatwoot_reusa_ticket_para_mesmo_assunto_e_cria_novo_para_outro(db_session):
    payload = payload_base(conversation_id="conv-multi-assunto", contact_id="contact-multi")

    with patch("Integrations.Chatwoot.service.Classifier", FakeClassifier):
        primeira = chamar_api("POST", "/integrations/chatwoot/messages", json=payload)
        segunda = chamar_api(
            "POST",
            "/integrations/chatwoot/messages",
            json={
                **payload,
                "message_id": "msg-mesmo-assunto",
                "message": "Ainda sobre eventos, como filtro por velocidade?",
            },
        )
        terceira = chamar_api(
            "POST",
            "/integrations/chatwoot/messages",
            json={
                **payload,
                "message_id": "msg-outro-assunto",
                "message": "Agora preciso revisar uma cobranca.",
            },
        )

    assert primeira.status_code == 200
    assert segunda.status_code == 200
    assert terceira.status_code == 200
    assert segunda.json()["ticket_id"] == primeira.json()["ticket_id"]
    assert segunda.json()["created_new_ticket"] is False
    assert terceira.json()["ticket_id"] != primeira.json()["ticket_id"]
    assert terceira.json()["created_new_ticket"] is True
    assert terceira.json()["category"] == "financeiro"


def test_chatwoot_cria_novo_ticket_quando_anterior_foi_fechado(db_session):
    payload = payload_base(conversation_id="conv-ticket-fechado", contact_id="contact-fechado")

    with patch("Integrations.Chatwoot.service.Classifier", FakeClassifier):
        primeira = chamar_api("POST", "/integrations/chatwoot/messages", json=payload)

    ticket = TicketRepository(db_session).obter_por_id(primeira.json()["ticket_id"])
    TicketRepository(db_session).atualizar_status(ticket, "closed")

    with patch("Integrations.Chatwoot.service.Classifier", FakeClassifier):
        segunda = chamar_api(
            "POST",
            "/integrations/chatwoot/messages",
            json={
                **payload,
                "message_id": "msg-ticket-fechado",
                "message": "Como vejo eventos novamente?",
            },
        )

    assert segunda.status_code == 200
    assert segunda.json()["ticket_id"] != primeira.json()["ticket_id"]
    assert segunda.json()["created_new_ticket"] is True
