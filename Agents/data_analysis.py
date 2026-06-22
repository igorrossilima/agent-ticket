import os
import sys
from typing import Dict, Iterable

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Agents.base import Agent


NOME_AGENTE_ANALISE_DADOS = "agente_analise_dados"


class DataAnalysis(Agent):
    def __init__(self, provedor_ia: str = "openai"):
        super().__init__(
            nome_agente=NOME_AGENTE_ANALISE_DADOS,
            provedor_ia=provedor_ia,
        )

    def executar(self, conversa: str) -> str:
        if not conversa or not conversa.strip():
            raise ValueError("O texto da conversa não pode ser vazio.")

        return self.executar_prompt(conversa=conversa.strip())

    def executar_arquivo_txt(self, caminho_arquivo: str) -> str:
        conversa = self._ler_arquivo_txt(caminho_arquivo)
        return self.executar(conversa)

    def executar_arquivos_txt(self, caminhos_arquivos: Iterable[str]) -> Dict[str, str]:
        return {
            caminho_arquivo: self.executar_arquivo_txt(caminho_arquivo)
            for caminho_arquivo in caminhos_arquivos
        }

    @staticmethod
    def _ler_arquivo_txt(caminho_arquivo: str) -> str:
        if not caminho_arquivo or not caminho_arquivo.strip():
            raise ValueError("O caminho do arquivo não pode ser vazio.")

        if not caminho_arquivo.lower().endswith(".txt"):
            raise ValueError("O arquivo da conversa precisa estar no formato .txt.")

        with open(caminho_arquivo, "r", encoding="utf-8") as file:
            return file.read()


def executar_analise_conversa(
    conversa: str,
    provedor_ia: str = "openai",
) -> str:
    analisador = DataAnalysis(provedor_ia=provedor_ia)
    return analisador.executar(conversa)


def executar_analise_conversa_txt(
    caminho_arquivo: str,
    provedor_ia: str = "openai",
) -> str:
    analisador = DataAnalysis(provedor_ia=provedor_ia)
    return analisador.executar_arquivo_txt(caminho_arquivo)


def executar_analise_conversas_txt(
    caminhos_arquivos: Iterable[str],
    provedor_ia: str = "openai",
) -> Dict[str, str]:
    analisador = DataAnalysis(provedor_ia=provedor_ia)
    return analisador.executar_arquivos_txt(caminhos_arquivos)


if __name__ == "__main__":
    conversa_teste = """
    Cliente: Fui cobrado duas vezes na minha assinatura.
    Atendente: Vou verificar a cobrança e abrir uma solicitação de estorno.
    Cliente: Obrigado.
    """
    resumo = executar_analise_conversa(conversa_teste, provedor_ia="openai")
    print(resumo)
