import unittest
from unittest.mock import patch

from Agents.base import Agent
from Agents.support import SupportAgent, executar_agente_suporte


class FakeModel:
    def __init__(self):
        self.prompt_sistema = None
        self.prompt_usuario = None

    def gerar_resposta(self, prompt_sistema: str, prompt_usuario: str) -> str:
        self.prompt_sistema = prompt_sistema
        self.prompt_usuario = prompt_usuario
        return "Resposta baseada no contexto da wiki."


class SupportAgentTest(unittest.TestCase):
    def test_carrega_prompt_do_agente_suporte(self):
        prompt = Agent.carregar_prompt(
            "Schemas/prompt_agente.yaml",
            "agente_suporte",
        )

        self.assertIn("agente de suporte da YUV", prompt["system"])
        self.assertIn("{mensagem_usuario}", prompt["user"])
        self.assertIn("{contexto_wiki}", prompt["user"])
        self.assertIn("{classificacao}", prompt["user"])

    def test_rejeita_mensagem_vazia(self):
        with patch("Agents.base.LLMFactory.criar_modelo", return_value=FakeModel()):
            agente = SupportAgent(provedor_ia="fake")

        with self.assertRaisesRegex(ValueError, "não pode ser vazia"):
            agente.executar(
                mensagem_usuario="   ",
                contexto_wiki="Contexto",
                classificacao={},
            )

    def test_gera_resposta_com_contexto_e_classificacao(self):
        modelo = FakeModel()

        with patch("Agents.base.LLMFactory.criar_modelo", return_value=modelo):
            agente = SupportAgent(provedor_ia="fake")

        resposta = agente.executar(
            mensagem_usuario="Como vejo eventos?",
            contexto_wiki="Eventos aparecem no relatório.",
            classificacao={"categoria": "suporte"},
        )

        self.assertEqual(resposta, "Resposta baseada no contexto da wiki.")
        self.assertIn("Como vejo eventos?", modelo.prompt_usuario)
        self.assertIn("Eventos aparecem no relatório.", modelo.prompt_usuario)
        self.assertIn('"categoria": "suporte"', modelo.prompt_usuario)

    def test_helper_executar_agente_suporte(self):
        with patch("Agents.base.LLMFactory.criar_modelo", return_value=FakeModel()):
            resposta = executar_agente_suporte(
                mensagem_usuario="Como vejo eventos?",
                contexto_wiki="Eventos aparecem no relatório.",
                classificacao={"categoria": "suporte"},
                provedor_ia="fake",
            )

        self.assertIn("Resposta baseada", resposta)


if __name__ == "__main__":
    unittest.main()
