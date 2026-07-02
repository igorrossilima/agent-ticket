import asyncio
import unittest
from uuid import UUID, uuid4

import httpx
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from Api.main import app, obter_executor_fluxo
from Customers.repository import CustomerRepository
from Postgres.config import obter_config_postgres
from Postgres.session import obter_sessao_db
from Tickets.repository import TicketMessageRepository, TicketRepository


class FakeFluxoExecutor:
    def __init__(self, resposta="Resposta final do agente."):
        self.resposta = resposta
        self.chamadas = []

    def __call__(self, **kwargs):
        self.chamadas.append(kwargs)
        return self.resposta


class ApiChatTest(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides = {}
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

    def tearDown(self):
        app.dependency_overrides = {}
        self.db_session.close()
        self.transaction.rollback()
        self.connection.close()
        self.engine.dispose()

    def sobrescrever_executor(self, executor):
        async def obter_executor_fake():
            return executor

        app.dependency_overrides[obter_executor_fluxo] = obter_executor_fake

    def auth_headers(self, token="token-usuario-teste"):
        return {"Authorization": f"Bearer {token}"}

    def criar_customer(self):
        sufixo = uuid4().hex
        return CustomerRepository(self.db_session).criar(
            name="Cliente Chat",
            email=f"cliente-chat-{sufixo}@example.com",
        )

    def chamar_api(self, method, path, json=None, headers=None):
        headers = self.auth_headers() if headers is None else headers

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

    def test_health_retorna_ok(self):
        resposta = self.chamar_api("GET", "/health")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), {"status": "ok"})

    def test_chat_com_mensagem_valida_chama_fluxo_e_retorna_resposta(self):
        executor = FakeFluxoExecutor()
        self.sobrescrever_executor(executor)
        customer = self.criar_customer()

        resposta = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "Como identifico equipamento offline?",
                "customer_id": str(customer.id),
                "top_k": 4,
                "provedor_ia": "openai",
            },
        )

        self.assertEqual(resposta.status_code, 200)
        ticket_id = UUID(resposta.json()["ticket_id"])
        self.assertEqual(
            resposta.json(),
            {
                "resposta": "Resposta final do agente.",
                "session_id": resposta.json()["session_id"],
                "ticket_id": resposta.json()["ticket_id"],
                "top_k": 4,
                "provedor_ia": "openai",
            },
        )
        self.assertTrue(resposta.json()["session_id"])
        self.assertEqual(executor.chamadas[0]["mensagem_usuario"], "Como identifico equipamento offline?")
        self.assertEqual(executor.chamadas[0]["top_k"], 4)
        self.assertEqual(executor.chamadas[0]["provedor_ia"], "openai")

        ticket = TicketRepository(self.db_session).obter_por_id(ticket_id)
        mensagens = TicketMessageRepository(self.db_session).listar_por_ticket(ticket_id)

        self.assertEqual(ticket.customer_id, customer.id)
        self.assertEqual(ticket.status, "pending")
        self.assertEqual([mensagem.sender_type for mensagem in mensagens], ["customer", "ai_agent"])
        self.assertEqual(mensagens[0].body, "Como identifico equipamento offline?")
        self.assertEqual(mensagens[1].body, "Resposta final do agente.")
        self.assertEqual(mensagens[1].metadata_["top_k"], 4)

    def test_chat_remove_espacos_extras_da_mensagem(self):
        executor = FakeFluxoExecutor()
        self.sobrescrever_executor(executor)
        customer = self.criar_customer()

        resposta = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "  Como vejo alarmes?  ",
                "customer_id": str(customer.id),
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(executor.chamadas[0]["mensagem_usuario"], "Como vejo alarmes?")

    def test_chat_com_mensagem_vazia_retorna_erro_400(self):
        customer = self.criar_customer()
        resposta = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "   ",
                "customer_id": str(customer.id),
            },
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("não pode ser vazia", resposta.json()["detail"])

    def test_chat_sem_token_retorna_erro_401(self):
        customer = self.criar_customer()
        resposta = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "Oi",
                "customer_id": str(customer.id),
            },
            headers={},
        )

        self.assertEqual(resposta.status_code, 401)
        self.assertIn("Token de autenticação", resposta.json()["detail"])

    def test_chat_com_token_invalido_retorna_erro_401(self):
        customer = self.criar_customer()
        resposta = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "Oi",
                "customer_id": str(customer.id),
            },
            headers={"Authorization": "Token abc"},
        )

        self.assertEqual(resposta.status_code, 401)
        self.assertIn("Bearer", resposta.json()["detail"])

    def test_chat_mantem_mesma_sessao_para_mesmo_token(self):
        executor = FakeFluxoExecutor()
        self.sobrescrever_executor(executor)
        customer = self.criar_customer()

        primeira_resposta = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "Primeira mensagem",
                "customer_id": str(customer.id),
            },
            headers=self.auth_headers("token-mesma-sessao"),
        )
        ticket_id = primeira_resposta.json()["ticket_id"]
        segunda_resposta = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "Segunda mensagem",
                "customer_id": str(customer.id),
                "ticket_id": ticket_id,
            },
            headers=self.auth_headers("token-mesma-sessao"),
        )

        self.assertEqual(primeira_resposta.status_code, 200)
        self.assertEqual(segunda_resposta.status_code, 200)
        self.assertEqual(
            primeira_resposta.json()["session_id"],
            segunda_resposta.json()["session_id"],
        )
        self.assertEqual(primeira_resposta.json()["ticket_id"], segunda_resposta.json()["ticket_id"])
        mensagens = TicketMessageRepository(self.db_session).listar_por_ticket(UUID(ticket_id))
        self.assertEqual(len(mensagens), 4)

    def test_chat_com_top_k_invalido_retorna_erro_de_validacao(self):
        customer = self.criar_customer()
        resposta_zero = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "Oi",
                "customer_id": str(customer.id),
                "top_k": 0,
            },
        )
        resposta_alto = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "Oi",
                "customer_id": str(customer.id),
                "top_k": 11,
            },
        )

        self.assertEqual(resposta_zero.status_code, 422)
        self.assertEqual(resposta_alto.status_code, 422)

    def test_chat_com_value_error_do_fluxo_retorna_400(self):
        def executor_com_erro(**kwargs):
            raise ValueError("Mensagem invalida para o fluxo.")

        self.sobrescrever_executor(executor_com_erro)
        customer = self.criar_customer()

        resposta = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "Oi",
                "customer_id": str(customer.id),
            },
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(resposta.json()["detail"], "Mensagem invalida para o fluxo.")

    def test_chat_com_erro_inesperado_do_fluxo_retorna_500_generico(self):
        def executor_com_erro(**kwargs):
            raise RuntimeError("segredo interno")

        self.sobrescrever_executor(executor_com_erro)
        customer = self.criar_customer()

        resposta = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "Oi",
                "customer_id": str(customer.id),
            },
        )

        self.assertEqual(resposta.status_code, 500)
        self.assertEqual(resposta.json()["detail"], "Erro interno ao processar a mensagem.")

    def test_chat_com_customer_inexistente_retorna_404(self):
        executor = FakeFluxoExecutor()
        self.sobrescrever_executor(executor)

        resposta = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "Oi",
                "customer_id": str(uuid4()),
            },
        )

        self.assertEqual(resposta.status_code, 404)
        self.assertIn("Cliente", resposta.json()["detail"])
        self.assertEqual(executor.chamadas, [])

    def test_chat_com_customer_diferente_do_ticket_retorna_400(self):
        executor = FakeFluxoExecutor()
        self.sobrescrever_executor(executor)
        customer_original = self.criar_customer()
        customer_diferente = self.criar_customer()

        primeira_resposta = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "Primeira mensagem",
                "customer_id": str(customer_original.id),
            },
        )
        resposta_invalida = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "Mensagem em ticket de outro cliente",
                "customer_id": str(customer_diferente.id),
                "ticket_id": primeira_resposta.json()["ticket_id"],
            },
        )

        self.assertEqual(resposta_invalida.status_code, 400)
        self.assertIn("nao pertence ao ticket", resposta_invalida.json()["detail"])


if __name__ == "__main__":
    unittest.main()
