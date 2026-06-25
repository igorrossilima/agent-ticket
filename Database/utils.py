import os
import uuid
from typing import Any, Dict, Iterable, List, Optional

from Database.chunkers import BaseChunker, Chunking
from Database.structure import DocumentoRAG
from models import BaseEmbeddingModel, EmbeddingFactory


class VectorDatabaseHelper:
    def __init__(
        self,
        db_connection_string: Optional[str] = None,
        collection_name: Optional[str] = None,
        embedding_model: Optional[BaseEmbeddingModel] = None,
        qdrant_client: Optional[Any] = None,
        vector_size: Optional[int] = None,
        criar_collection: bool = False,
    ):
        self.connection = db_connection_string or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.collection_name = collection_name or os.getenv(
            "QDRANT_COLLECTION",
            "documentos_empresa",
        )
        self.embedding_model = embedding_model or EmbeddingFactory.criar_modelo("openai")
        self.vector_size = vector_size or self._resolver_vector_size()
        self.client = qdrant_client or self._criar_qdrant_client()

        if criar_collection:
            self.criar_collection_se_nao_existir()

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

    def indexar_documento(self, documento: DocumentoRAG) -> None:
        self.indexar_documentos([documento])

    def indexar_texto(
        self,
        texto: str,
        documento_id: str,
        metadados: Optional[Dict[str, Any]] = None,
        chunker: Optional[BaseChunker] = None,
    ) -> List[DocumentoRAG]:
        documentos = Chunking(chunker=chunker).gerar_documentos(
            texto=texto,
            documento_id=documento_id,
            metadados=metadados,
        )
        self.indexar_documentos(documentos)

        return documentos

    def indexar_documentos(self, documentos: Iterable[DocumentoRAG]) -> None:
        documentos = list(documentos)

        if not documentos:
            raise ValueError("A lista de documentos não pode ser vazia.")

        textos = [documento.text for documento in documentos]
        embeddings = self.embedding_model.gerar_embeddings(textos)

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

    def buscar_contexto_relevante(self, query_usuario: str, top_k: int = 3) -> List[str]:
        documentos = self.buscar_documentos_relevantes(
            query_usuario=query_usuario,
            top_k=top_k,
        )

        return [documento.text for documento in documentos]

    def buscar_documentos_relevantes(
        self,
        query_usuario: str,
        top_k: int = 3,
        filtro: Optional[Any] = None,
    ) -> List[DocumentoRAG]:
        if not query_usuario or not query_usuario.strip():
            raise ValueError("A query do usuário não pode ser vazia.")

        embedding_query = self.embedding_model.gerar_embedding(query_usuario.strip())
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

        payload = self._criar_payload(documento)

        return models.PointStruct(
            id=self._gerar_point_id(documento.id),
            vector=embedding,
            payload=payload,
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
