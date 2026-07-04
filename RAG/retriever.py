from typing import Any, List, Optional

from RAG.structure import DocumentoRAG
from RAG.vector_store import QdrantVectorStore
from AI.embeddings import BaseEmbeddingModel


class DocumentRetriever:
    def __init__(
        self,
        vector_store: QdrantVectorStore,
        embedding_model: BaseEmbeddingModel,
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    def buscar_documentos_relevantes(
        self,
        query_usuario: str,
        top_k: int = 3,
        filtro: Optional[Any] = None,
    ) -> List[DocumentoRAG]:
        if not query_usuario or not query_usuario.strip():
            raise ValueError("A query do usuário não pode ser vazia.")

        embedding_query = self.embedding_model.gerar_embedding(query_usuario.strip())

        return self.vector_store.buscar_por_embedding(
            embedding_query=embedding_query,
            top_k=top_k,
            filtro=filtro,
        )
