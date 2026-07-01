import asyncio
import unittest
from unittest.mock import patch

import httpx

from Api.main import app
from Database.structure import DocumentoRAG


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

    def tearDown(self):
        app.dependency_overrides = {}

    def chamar_chat(self, token="token-e2e"):
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
                        "top_k": 2,
                        "provedor_ia": "openai",
                    },
                )

        return asyncio.run(executar())

    def test_chat_executa_fluxo_completo_com_sessao_worker_agents_e_retriever(self):
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
        self.assertTrue(corpo["session_id"])
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
