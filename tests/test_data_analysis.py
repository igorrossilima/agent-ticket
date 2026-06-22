import os
import tempfile
import unittest
from unittest.mock import patch

from Agents.base import Agent
from Agents.data_analysis import DataAnalysis


class FakeModel:
    def gerar_resposta(self, prompt_sistema: str, prompt_usuario: str) -> str:
        return "Cliente pediu estorno por cobrança duplicada. Atendimento abriu solicitação."


class DataAnalysisTest(unittest.TestCase):
    def test_carrega_prompt_do_agente_de_analise(self):
        prompt = Agent.carregar_prompt(
            "Schemas/prompt_agente.yaml",
            "agente_analise_dados",
        )

        self.assertIn("conversas de atendimento", prompt["system"])
        self.assertIn("{conversa}", prompt["user"])

    def test_rejeita_conversa_vazia(self):
        with patch("Agents.base.LLMFactory.criar_modelo", return_value=FakeModel()):
            analisador = DataAnalysis(provedor_ia="fake")

        with self.assertRaisesRegex(ValueError, "não pode ser vazio"):
            analisador.executar("   ")

    def test_gera_resumo_da_conversa(self):
        with patch("Agents.base.LLMFactory.criar_modelo", return_value=FakeModel()):
            analisador = DataAnalysis(provedor_ia="fake")

        resultado = analisador.executar(
            "Cliente: Fui cobrado duas vezes.\nAtendente: Vou abrir estorno."
        )

        self.assertIn("cobrança duplicada", resultado)
        self.assertIn("estorno", resultado)

    def test_gera_resumo_de_arquivo_txt(self):
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            encoding="utf-8",
            delete=False,
        ) as file:
            file.write("Cliente: Fui cobrado duas vezes.")
            caminho_arquivo = file.name

        try:
            with patch("Agents.base.LLMFactory.criar_modelo", return_value=FakeModel()):
                analisador = DataAnalysis(provedor_ia="fake")

            resultado = analisador.executar_arquivo_txt(caminho_arquivo)

            self.assertIn("estorno", resultado)
        finally:
            os.remove(caminho_arquivo)

    def test_rejeita_arquivo_que_nao_e_txt(self):
        with patch("Agents.base.LLMFactory.criar_modelo", return_value=FakeModel()):
            analisador = DataAnalysis(provedor_ia="fake")

        with self.assertRaisesRegex(ValueError, "formato .txt"):
            analisador.executar_arquivo_txt("conversa.pdf")


if __name__ == "__main__":
    unittest.main()
