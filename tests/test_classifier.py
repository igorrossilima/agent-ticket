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


class FakeModelCategoriaInvalida:
    def gerar_resposta(self, prompt_sistema: str, prompt_usuario: str) -> str:
        return """
        {
          "categoria": "categoria_que_nao_existe",
          "confianca": 2.4,
          "intencao": "",
          "termos_busca": "",
          "justificativa": ""
        }
        """


class ClassifierTest(unittest.TestCase):
    def test_carrega_prompt_do_classificador(self):
        prompt = Agent.carregar_prompt(
            "Agents/prompts/prompt_agente.yaml",
            "agente_classificador",
        )

        self.assertIn("Classifique o ticket", prompt["system"])
        self.assertIn("- rastreamento", prompt["system"])
        self.assertIn("- eventos", prompt["system"])
        self.assertIn("- acesso", prompt["system"])
        self.assertIn('"intencao"', prompt["system"])
        self.assertIn('"termos_busca"', prompt["system"])
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
        self.assertEqual(resultado["intencao"], "nao_identificada")
        self.assertEqual(resultado["termos_busca"], [])
        self.assertIn("cobrança duplicada", resultado["justificativa"])

    def test_normaliza_categoria_invalida_e_confianca_fora_do_intervalo(self):
        with patch("Agents.base.LLMFactory.criar_modelo", return_value=FakeModelCategoriaInvalida()):
            classificador = Classifier(provedor_ia="fake")

        resultado = classificador.executar("Pergunta muito aberta.")

        self.assertEqual(resultado["categoria"], "outros")
        self.assertEqual(resultado["confianca"], 1.0)
        self.assertEqual(resultado["intencao"], "nao_identificada")


if __name__ == "__main__":
    unittest.main()
