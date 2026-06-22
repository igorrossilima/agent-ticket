import unittest
from unittest.mock import patch

from Agents.base import Agent
from Agents.classifier import Classifier


class FakeModel:
    def gerar_resposta(self, prompt_sistema: str, prompt_usuario: str) -> str:
        return """
        Texto antes do JSON.
        {
          "categoria": "financeiro",
          "confianca": 0.95,
          "justificativa": "O ticket fala sobre cobrança duplicada."
        }
        """


class ClassifierTest(unittest.TestCase):
    def test_carrega_prompt_do_classificador(self):
        prompt = Agent.carregar_prompt(
            "Schemas/prompt_agente.yaml",
            "agente_classificador",
        )

        self.assertIn("Classifique o ticket", prompt["system"])
        self.assertIn("{ticket}", prompt["user"])

    def test_rejeita_ticket_vazio(self):
        with patch("Agents.base.LLMFactory.criar_modelo", return_value=FakeModel()):
            classificador = Classifier(provedor_ia="fake")

        with self.assertRaisesRegex(ValueError, "não pode ser vazio"):
            classificador.executar("   ")

    def test_classifica_ticket_com_json_extraido_da_resposta(self):
        with patch("Agents.base.LLMFactory.criar_modelo", return_value=FakeModel()):
            classificador = Classifier(provedor_ia="fake")

        resultado = classificador.executar(
            "Quero cancelar porque fui cobrado duas vezes."
        )

        self.assertEqual(resultado["categoria"], "financeiro")
        self.assertEqual(resultado["confianca"], 0.95)
        self.assertIn("cobrança duplicada", resultado["justificativa"])


if __name__ == "__main__":
    unittest.main()
