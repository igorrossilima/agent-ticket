import asyncio
import unittest

import httpx

from Api.main import app, obter_executor_fluxo


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

    def tearDown(self):
        app.dependency_overrides = {}

    def sobrescrever_executor(self, executor):
        async def obter_executor_fake():
            return executor

        app.dependency_overrides[obter_executor_fluxo] = obter_executor_fake

    def chamar_api(self, method, path, json=None):
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

    def test_health_retorna_ok(self):
        resposta = self.chamar_api("GET", "/health")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), {"status": "ok"})

    def test_chat_com_mensagem_valida_chama_fluxo_e_retorna_resposta(self):
        executor = FakeFluxoExecutor()
        self.sobrescrever_executor(executor)

        resposta = self.chamar_api(
            "POST",
            "/chat",
            json={
                "mensagem": "Como identifico equipamento offline?",
                "top_k": 4,
                "provedor_ia": "openai",
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.json(),
            {
                "resposta": "Resposta final do agente.",
                "top_k": 4,
                "provedor_ia": "openai",
            },
        )
        self.assertEqual(executor.chamadas[0]["mensagem_usuario"], "Como identifico equipamento offline?")
        self.assertEqual(executor.chamadas[0]["top_k"], 4)
        self.assertEqual(executor.chamadas[0]["provedor_ia"], "openai")

    def test_chat_remove_espacos_extras_da_mensagem(self):
        executor = FakeFluxoExecutor()
        self.sobrescrever_executor(executor)

        resposta = self.chamar_api(
            "POST",
            "/chat",
            json={"mensagem": "  Como vejo alarmes?  "},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(executor.chamadas[0]["mensagem_usuario"], "Como vejo alarmes?")

    def test_chat_com_mensagem_vazia_retorna_erro_400(self):
        resposta = self.chamar_api("POST", "/chat", json={"mensagem": "   "})

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("não pode ser vazia", resposta.json()["detail"])

    def test_chat_com_top_k_invalido_retorna_erro_de_validacao(self):
        resposta_zero = self.chamar_api("POST", "/chat", json={"mensagem": "Oi", "top_k": 0})
        resposta_alto = self.chamar_api("POST", "/chat", json={"mensagem": "Oi", "top_k": 11})

        self.assertEqual(resposta_zero.status_code, 422)
        self.assertEqual(resposta_alto.status_code, 422)

    def test_chat_com_value_error_do_fluxo_retorna_400(self):
        def executor_com_erro(**kwargs):
            raise ValueError("Mensagem invalida para o fluxo.")

        self.sobrescrever_executor(executor_com_erro)

        resposta = self.chamar_api("POST", "/chat", json={"mensagem": "Oi"})

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(resposta.json()["detail"], "Mensagem invalida para o fluxo.")

    def test_chat_com_erro_inesperado_do_fluxo_retorna_500_generico(self):
        def executor_com_erro(**kwargs):
            raise RuntimeError("segredo interno")

        self.sobrescrever_executor(executor_com_erro)

        resposta = self.chamar_api("POST", "/chat", json={"mensagem": "Oi"})

        self.assertEqual(resposta.status_code, 500)
        self.assertEqual(resposta.json()["detail"], "Erro interno ao processar a mensagem.")


if __name__ == "__main__":
    unittest.main()
