from typing import Any, Dict, Iterable, List, Optional

from Database.chunkers import BaseChunker
from Database.indexer import DocumentIndexer
from Database.retriever import DocumentRetriever
from Database.structure import DocumentoRAG
from Database.vector_store import QdrantVectorStore
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
        self.embedding_model = embedding_model or EmbeddingFactory.criar_modelo("openai")
        self.vector_store = QdrantVectorStore(
            db_connection_string=db_connection_string,
            collection_name=collection_name,
            qdrant_client=qdrant_client,
            vector_size=vector_size,
        )
        self.indexer = DocumentIndexer(
            vector_store=self.vector_store,
            embedding_model=self.embedding_model,
        )
        self.retriever = DocumentRetriever(
            vector_store=self.vector_store,
            embedding_model=self.embedding_model,
        )
        self.connection = self.vector_store.connection
        self.collection_name = self.vector_store.collection_name
        self.vector_size = self.vector_store.vector_size
        self.client = self.vector_store.client

        if criar_collection:
            self.criar_collection_se_nao_existir()

    def criar_collection_se_nao_existir(self) -> None:
        self.vector_store.criar_collection_se_nao_existir()

    def indexar_documento(self, documento: DocumentoRAG) -> None:
        self.indexer.indexar_documento(documento)

    def indexar_texto(
        self,
        texto: str,
        documento_id: str,
        metadados: Optional[Dict[str, Any]] = None,
        chunker: Optional[BaseChunker] = None,
    ) -> List[DocumentoRAG]:
        return self.indexer.indexar_texto(
            texto=texto,
            documento_id=documento_id,
            metadados=metadados,
            chunker=chunker,
        )

    def indexar_documentos(self, documentos: Iterable[DocumentoRAG]) -> None:
        self.indexer.indexar_documentos(documentos)

    def buscar_contexto_relevante(self, query_usuario: str, top_k: int = 3) -> List[str]:
        return self.retriever.buscar_contexto_relevante(
            query_usuario=query_usuario,
            top_k=top_k,
        )

    def buscar_documentos_relevantes(
        self,
        query_usuario: str,
        top_k: int = 3,
        filtro: Optional[Any] = None,
    ) -> List[DocumentoRAG]:
        return self.retriever.buscar_documentos_relevantes(
            query_usuario=query_usuario,
            top_k=top_k,
            filtro=filtro,
        )
