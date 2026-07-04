import os
from abc import ABC, abstractmethod
from typing import List, Optional


class BaseEmbeddingModel(ABC):
    @abstractmethod
    def gerar_embedding(self, texto: str) -> List[float]:
        pass

    def gerar_embeddings(self, textos: List[str]) -> List[List[float]]:
        return [self.gerar_embedding(texto) for texto in textos]


class OpenAIEmbeddingModel(BaseEmbeddingModel):
    def __init__(self, modelo: Optional[str] = None, dimensions: Optional[int] = None):
        from openai import OpenAI

        self.client = OpenAI()
        self.modelo = modelo or os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self.dimensions = self._resolver_dimensions(dimensions)

    def gerar_embedding(self, texto: str) -> List[float]:
        if not texto or not texto.strip():
            raise ValueError("O texto para embedding não pode ser vazio.")

        return self.gerar_embeddings([texto.strip()])[0]

    def gerar_embeddings(self, textos: List[str]) -> List[List[float]]:
        textos_limpos = []

        for texto in textos:
            if not texto or not texto.strip():
                raise ValueError("Os textos para embedding não podem conter valores vazios.")

            textos_limpos.append(texto.strip())

        if not textos_limpos:
            raise ValueError("A lista de textos para embedding não pode ser vazia.")

        parametros = {
            "model": self.modelo,
            "input": textos_limpos,
        }

        if self.dimensions:
            parametros["dimensions"] = self.dimensions

        response = self.client.embeddings.create(**parametros)
        print("[Log] Gerando embeddings com OpenAI...")

        dados_ordenados = sorted(response.data, key=lambda item: item.index)
        return [item.embedding for item in dados_ordenados]

    @staticmethod
    def _resolver_dimensions(dimensions: Optional[int]) -> Optional[int]:
        valor = dimensions if dimensions is not None else os.getenv("OPENAI_EMBEDDING_DIMENSIONS")

        if valor in (None, ""):
            return None

        return int(valor)


class EmbeddingFactory:
    @staticmethod
    def criar_modelo(provedor_ia: str = "openai") -> BaseEmbeddingModel:
        if provedor_ia.lower() == "openai":
            return OpenAIEmbeddingModel()

        raise ValueError(f"Provedor de embedding não suportado:/n{provedor_ia}")
