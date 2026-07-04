import asyncio
import unittest
from uuid import uuid4
from unittest.mock import patch

import httpx
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from Api.main import app
from Auth.token_service import TokenService
from Customers.repository import CustomerRepository
from RAG.structure import DocumentoRAG
from Postgres.config import obter_config_postgres
from Postgres.session import obter_sessao_db
from Users.repository import UserRepository


class FakeModel:
    def __init__(self):
        self.chamadas = []

    def gerar_resposta(self, prompt_sistema: str, prompt_usuario: str) -> str:
        self.chamadas.append(
            {
                "prompt_sistema": prompt_sistema,
                "prompt_usuario": prompt_usuario,
            }
        )

        if "classificador de tickets" in prompt_sistema:
            return """
            {
                "categoria": "suporte",
                "confianca": 0.92,
                "justificativa": "Cliente quer consultar eventos.",
                "intencao": "consultar_eventos",
                "termos_busca": ["eventos", "velocidade"]
            }
            """

        return "O sistema permite consultar eventos usando os filtros da tela de eventos."


class FakeVectorDatabaseHelper:
    instances = []

    def __init__(self):
        self.query_usuario = None
        self.top_k = None
        FakeVectorDatabaseHelper.instances.append(self)

    def buscar_documentos_relevantes(self, query_usuario: str, top_k: int = 3):
        self.query_usuario = query_usuario
        self.top_k = top_k

        return [
            DocumentoRAG(
                id="wiki-eventos-1",
                text="Eventos de velocidade ficam disponiveis na tela de eventos.",
                metadados={"documento_origem_id": "wiki-eventos"},
                score=0.98,
            )
        ]


class ChatE2ETest(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides = {}
        FakeVectorDatabaseHelper.instances = []
        self.engine = create_engine(obter_config_postgres().database_url, pool_pre_ping=True)
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        self.SessionLocal = sessionmaker(
            bind=self.connection,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        self.db_session = self.SessionLocal()
        self.nested = self.connection.begin_nested()

        @event.listens_for(self.db_session, "after_transaction_end")
        def reiniciar_savepoint(session, transaction):
            if not self.nested.is_active:
                self.nested = self.connection.begin_nested()

        def sobrescrever_sessao_db():
            yield self.db_session

        app.dependency_overrides[obter_sessao_db] = sobrescrever_sessao_db
        self.auth_user = UserRepository(self.db_session).criar(
            name="Usuario E2E",
            email=f"e2e-{uuid4().hex}@example.com",
            password_hash="hash-teste",
            role="admin",
        )
        self.access_token = TokenService().criar_access_token(self.auth_user)
        self.customer = CustomerRepository(self.db_session).criar(
            name="Cliente E2E",
            email=f"cliente-e2e-{uuid4().hex}@example.com",
        )

    def tearDown(self):
        app.dependency_overrides = {}
        self.db_session.close()
        self.transaction.rollback()
        self.connection.close()
        self.engine.dispose()

    def chamar_chat(self, token=None):
        token = token or self.access_token

        async def executar():
            transport = httpx.ASGITransport(
                app=app,
                raise_app_exceptions=False,
            )
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
            ) as client:
                return await client.post(
                    "/chat",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "mensagem": "Como vejo eventos de velocidade?",
                        "customer_id": str(self.customer.id),
                        "top_k": 2,
                        "provedor_ia": "openai",
                    },
                )

        return asyncio.run(executar())

    def test_chat_executa_fluxo_completo_com_ticket_worker_agents_e_retriever(self):
        modelo = FakeModel()

        with patch("Agents.base.LLMFactory.criar_modelo", return_value=modelo), patch(
            "Workers.main.VectorDatabaseHelper",
            FakeVectorDatabaseHelper,
        ):
            resposta = self.chamar_chat()

        self.assertEqual(resposta.status_code, 200)
        corpo = resposta.json()

        self.assertEqual(
            corpo["resposta"],
            "O sistema permite consultar eventos usando os filtros da tela de eventos.",
        )
        self.assertTrue(corpo["ticket_id"])
        self.assertEqual(corpo["top_k"], 2)
        self.assertEqual(corpo["provedor_ia"], "openai")

        self.assertEqual(len(modelo.chamadas), 2)
        self.assertIn("Ticket:", modelo.chamadas[0]["prompt_usuario"])
        self.assertIn("Contexto da wiki:", modelo.chamadas[1]["prompt_usuario"])
        self.assertIn("Eventos de velocidade", modelo.chamadas[1]["prompt_usuario"])

        db = FakeVectorDatabaseHelper.instances[0]
        self.assertEqual(db.top_k, 2)
        self.assertIn("Como vejo eventos de velocidade?", db.query_usuario)
        self.assertIn("suporte", db.query_usuario)
        self.assertIn("velocidade", db.query_usuario)


if __name__ == "__main__":
    unittest.main()
