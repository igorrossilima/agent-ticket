import os
import uuid
from typing import Any, Dict, Iterable, List, Optional

from Database.structure import DocumentoRAG


class QdrantVectorStore:
    def __init__(
        self,
        db_connection_string: Optional[str] = None,
        collection_name: Optional[str] = None,
        qdrant_client: Optional[Any] = None,
        vector_size: Optional[int] = None,
    ):
        self.connection = db_connection_string or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.collection_name = collection_name or os.getenv(
            "QDRANT_COLLECTION",
            "documentos_empresa",
        )
        self.vector_size = vector_size or self._resolver_vector_size()
        self.client = qdrant_client or self._criar_qdrant_client()

    def criar_collection_se_nao_existir(self) -> None:
        if self._collection_existe():
            return

        from qdrant_client import models

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=self.vector_size,
                distance=models.Distance.COSINE,
            ),
        )

    def upsert_documentos(
        self,
        documentos: Iterable[DocumentoRAG],
        embeddings: Iterable[List[float]],
    ) -> None:
        documentos = list(documentos)
        embeddings = list(embeddings)

        if len(embeddings) != len(documentos):
            raise ValueError("A quantidade de embeddings precisa bater com a quantidade de documentos.")

        pontos = [
            self._criar_ponto_qdrant(documento=documento, embedding=embedding)
            for documento, embedding in zip(documentos, embeddings)
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=pontos,
        )

    def buscar_por_embedding(
        self,
        embedding_query: List[float],
        top_k: int = 3,
        filtro: Optional[Any] = None,
    ) -> List[DocumentoRAG]:
        parametros = {
            "collection_name": self.collection_name,
            "query": embedding_query,
            "limit": top_k,
            "with_payload": True,
        }

        if filtro is not None:
            parametros["query_filter"] = filtro

        resposta = self.client.query_points(**parametros)
        pontos = getattr(resposta, "points", resposta)

        return [self._documento_from_ponto(ponto) for ponto in pontos]

    def _criar_qdrant_client(self) -> Any:
        from qdrant_client import QdrantClient

        api_key = os.getenv("QDRANT_API_KEY")

        if api_key:
            return QdrantClient(url=self.connection, api_key=api_key)

        return QdrantClient(url=self.connection)

    def _collection_existe(self) -> bool:
        try:
            self.client.get_collection(collection_name=self.collection_name)
            return True
        except Exception:
            return False

    def _criar_ponto_qdrant(self, documento: DocumentoRAG, embedding: List[float]) -> Any:
        from qdrant_client import models

        return models.PointStruct(
            id=self._gerar_point_id(documento.id),
            vector=embedding,
            payload=self._criar_payload(documento),
        )

    @staticmethod
    def _criar_payload(documento: DocumentoRAG) -> Dict[str, Any]:
        return {
            "documento_id": documento.id,
            "text": documento.text,
            "metadados": documento.metadados,
        }

    @staticmethod
    def _documento_from_ponto(ponto: Any) -> DocumentoRAG:
        payload = getattr(ponto, "payload", {}) or {}

        return DocumentoRAG(
            id=payload.get("documento_id", str(getattr(ponto, "id", ""))),
            text=payload.get("text", ""),
            metadados=payload.get("metadados", {}),
            score=getattr(ponto, "score", None),
        )

    @staticmethod
    def _gerar_point_id(documento_id: str) -> str:
        try:
            return str(uuid.UUID(documento_id))
        except ValueError:
            return str(uuid.uuid5(uuid.NAMESPACE_URL, documento_id))

    @staticmethod
    def _resolver_vector_size() -> int:
        valor = os.getenv("QDRANT_VECTOR_SIZE") or os.getenv("OPENAI_EMBEDDING_DIMENSIONS")

        if valor:
            return int(valor)

        return 1536
