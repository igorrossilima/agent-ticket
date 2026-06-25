import math
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from Database.structure import DocumentoRAG
from models import BaseEmbeddingModel


class BaseChunker(ABC):
    @abstractmethod
    def gerar_chunks(self, texto: str) -> List[str]:
        pass

    @staticmethod
    def _validar_texto(texto: str) -> str:
        if not texto or not texto.strip():
            raise ValueError("O texto para chunking não pode ser vazio.")

        return texto.strip()


class RecursiveChunker(BaseChunker):
    def __init__(
        self,
        tamanho_chunk: int = 1000,
        sobreposicao: int = 100,
        separadores: Optional[List[str]] = None,
    ):
        if tamanho_chunk <= 0:
            raise ValueError("O tamanho do chunk precisa ser maior que zero.")

        if sobreposicao < 0:
            raise ValueError("A sobreposição não pode ser negativa.")

        if sobreposicao >= tamanho_chunk:
            raise ValueError("A sobreposição precisa ser menor que o tamanho do chunk.")

        self.tamanho_chunk = tamanho_chunk
        self.sobreposicao = sobreposicao
        self.separadores = separadores or ["\n\n", "\n", ". ", " ", ""]

    def gerar_chunks(self, texto: str) -> List[str]:
        texto = self._validar_texto(texto)
        partes = self._dividir_recursivamente(texto, self.separadores)
        chunks = self._juntar_partes(partes)

        return [chunk for chunk in chunks if chunk]

    def _dividir_recursivamente(self, texto: str, separadores: List[str]) -> List[str]:
        if len(texto) <= self.tamanho_chunk:
            return [texto.strip()]

        separador = separadores[0]
        proximos_separadores = separadores[1:]

        if separador == "":
            return [
                texto[indice : indice + self.tamanho_chunk].strip()
                for indice in range(0, len(texto), self.tamanho_chunk)
            ]

        partes = texto.split(separador)

        if len(partes) == 1:
            return self._dividir_recursivamente(texto, proximos_separadores)

        resultado = []
        for parte in partes:
            parte = parte.strip()

            if not parte:
                continue

            if len(parte) > self.tamanho_chunk:
                resultado.extend(self._dividir_recursivamente(parte, proximos_separadores))
            else:
                resultado.append(parte)

        return resultado

    def _juntar_partes(self, partes: List[str]) -> List[str]:
        chunks = []
        chunk_atual = ""

        for parte in partes:
            candidato = f"{chunk_atual} {parte}".strip() if chunk_atual else parte

            if len(candidato) <= self.tamanho_chunk:
                chunk_atual = candidato
                continue

            if chunk_atual:
                chunks.append(chunk_atual)

            chunk_atual = self._aplicar_sobreposicao(chunk_atual, parte)

        if chunk_atual:
            chunks.append(chunk_atual)

        return chunks

    def _aplicar_sobreposicao(self, chunk_anterior: str, proxima_parte: str) -> str:
        if not self.sobreposicao or not chunk_anterior:
            return proxima_parte

        sobreposicao_texto = chunk_anterior[-self.sobreposicao :].strip()
        candidato = f"{sobreposicao_texto} {proxima_parte}".strip()

        if len(candidato) <= self.tamanho_chunk:
            return candidato

        return proxima_parte


class SemanticChunker(BaseChunker):
    def __init__(
        self,
        embedding_model: BaseEmbeddingModel,
        tamanho_chunk: int = 1000,
        limite_similaridade: float = 0.75,
    ):
        if tamanho_chunk <= 0:
            raise ValueError("O tamanho do chunk precisa ser maior que zero.")

        if not 0 <= limite_similaridade <= 1:
            raise ValueError("O limite de similaridade precisa estar entre 0 e 1.")

        self.embedding_model = embedding_model
        self.tamanho_chunk = tamanho_chunk
        self.limite_similaridade = limite_similaridade

    def gerar_chunks(self, texto: str) -> List[str]:
        texto = self._validar_texto(texto)
        sentencas = self._dividir_sentencas(texto)

        if len(sentencas) <= 1:
            return sentencas

        embeddings = self.embedding_model.gerar_embeddings(sentencas)
        chunks = []
        chunk_atual = sentencas[0]

        for indice in range(1, len(sentencas)):
            sentenca = sentencas[indice]
            similaridade = self._similaridade_cosseno(
                embeddings[indice - 1],
                embeddings[indice],
            )
            candidato = f"{chunk_atual} {sentenca}".strip()

            if similaridade >= self.limite_similaridade and len(candidato) <= self.tamanho_chunk:
                chunk_atual = candidato
                continue

            chunks.append(chunk_atual)
            chunk_atual = sentenca

        if chunk_atual:
            chunks.append(chunk_atual)

        return chunks

    @staticmethod
    def _dividir_sentencas(texto: str) -> List[str]:
        sentencas = re.split(r"(?<=[.!?])\s+", texto.strip())
        return [sentenca.strip() for sentenca in sentencas if sentenca.strip()]

    @staticmethod
    def _similaridade_cosseno(vetor_a: List[float], vetor_b: List[float]) -> float:
        produto = sum(a * b for a, b in zip(vetor_a, vetor_b))
        norma_a = math.sqrt(sum(a * a for a in vetor_a))
        norma_b = math.sqrt(sum(b * b for b in vetor_b))

        if norma_a == 0 or norma_b == 0:
            return 0.0

        return produto / (norma_a * norma_b)


class Chunking:
    def __init__(self, chunker: Optional[BaseChunker] = None):
        self.chunker = chunker or RecursiveChunker()

    def gerar_chunks(self, texto: str) -> List[str]:
        return self.chunker.gerar_chunks(texto)

    def gerar_documentos(
        self,
        texto: str,
        documento_id: str,
        metadados: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentoRAG]:
        chunks = self.gerar_chunks(texto)
        metadados = metadados or {}

        return [
            DocumentoRAG(
                id=f"{documento_id}-chunk-{indice + 1}",
                text=chunk,
                metadados={
                    **metadados,
                    "documento_origem_id": documento_id,
                    "chunk_indice": indice,
                    "chunk_total": len(chunks),
                },
            )
            for indice, chunk in enumerate(chunks)
        ]
