from typing import Any, Dict, Iterable, List, Optional

from Database.chunkers import BaseChunker, Chunking
from Database.structure import DocumentoRAG
from Database.vector_store import QdrantVectorStore
from models import BaseEmbeddingModel


class DocumentIndexer:
    def __init__(
        self,
        vector_store: QdrantVectorStore,
        embedding_model: BaseEmbeddingModel,
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model

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

        self.vector_store.upsert_documentos(
            documentos=documentos,
            embeddings=embeddings,
        )
