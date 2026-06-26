import importlib.util
import unittest

from Database.structure import DocumentoRAG
from Database.indexer import DocumentIndexer
from Database.retriever import DocumentRetriever
from Database.utils import VectorDatabaseHelper
from Database.vector_store import QdrantVectorStore
from models import BaseEmbeddingModel


class FakeEmbeddingModel(BaseEmbeddingModel):
    def gerar_embedding(self, texto):
        return [0.1, 0.2, 0.3]

    def gerar_embeddings(self, textos):
        return [[0.1, 0.2, 0.3] for _ in textos]


class FakePoint:
    id = "point-id"
    score = 0.98
    payload = {
        "documento_id": "politica_reembolso",
        "text": "O cliente pode pedir reembolso em ate 7 dias.",
        "metadados": {"categoria": "financeiro"},
    }


class FakeQueryResponse:
    points = [FakePoint()]


class FakeQdrantClient:
    def __init__(self):
        self.query_kwargs = None
        self.upsert_kwargs = None

    def query_points(self, **kwargs):
        self.query_kwargs = kwargs
        return FakeQueryResponse()

    def upsert(self, **kwargs):
        self.upsert_kwargs = kwargs


class FakeVectorStore:
    def __init__(self):
        self.upsert_documentos_kwargs = None
        self.buscar_por_embedding_kwargs = None

    def upsert_documentos(self, documentos, embeddings):
        self.upsert_documentos_kwargs = {
            "documentos": list(documentos),
            "embeddings": list(embeddings),
        }

    def buscar_por_embedding(self, embedding_query, top_k=3, filtro=None):
        self.buscar_por_embedding_kwargs = {
            "embedding_query": embedding_query,
            "top_k": top_k,
            "filtro": filtro,
        }
        return [
            DocumentoRAG(
                id="politica_reembolso",
                text="O cliente pode pedir reembolso em ate 7 dias.",
                metadados={"categoria": "financeiro"},
                score=0.98,
            )
        ]


class VectorDatabaseHelperTest(unittest.TestCase):
    def test_documento_rag_aceita_metadados_embedding_e_score(self):
        documento = DocumentoRAG(
            id="doc-1",
            text="Politica interna de suporte.",
            metadados={"fonte": "manual"},
            embedding=[0.1, 0.2],
            score=0.9,
        )

        self.assertEqual(documento.id, "doc-1")
        self.assertEqual(documento.metadados["fonte"], "manual")
        self.assertEqual(documento.embedding, [0.1, 0.2])
        self.assertEqual(documento.score, 0.9)

    def test_busca_contexto_relevante_consulta_qdrant_com_embedding_da_query(self):
        qdrant_client = FakeQdrantClient()
        helper = VectorDatabaseHelper(
            collection_name="documentos_teste",
            embedding_model=FakeEmbeddingModel(),
            qdrant_client=qdrant_client,
            vector_size=3,
        )

        contexto = helper.buscar_contexto_relevante("Como funciona reembolso?", top_k=1)

        self.assertEqual(contexto, ["O cliente pode pedir reembolso em ate 7 dias."])
        self.assertEqual(qdrant_client.query_kwargs["collection_name"], "documentos_teste")
        self.assertEqual(qdrant_client.query_kwargs["query"], [0.1, 0.2, 0.3])
        self.assertEqual(qdrant_client.query_kwargs["limit"], 1)
        self.assertTrue(qdrant_client.query_kwargs["with_payload"])

    def test_helper_mantem_fachada_com_indexer_retriever_e_vector_store(self):
        qdrant_client = FakeQdrantClient()
        helper = VectorDatabaseHelper(
            collection_name="documentos_teste",
            embedding_model=FakeEmbeddingModel(),
            qdrant_client=qdrant_client,
            vector_size=3,
        )

        self.assertIsInstance(helper.vector_store, QdrantVectorStore)
        self.assertIsInstance(helper.indexer, DocumentIndexer)
        self.assertIsInstance(helper.retriever, DocumentRetriever)
        self.assertIs(helper.client, qdrant_client)
        self.assertEqual(helper.collection_name, "documentos_teste")

    @unittest.skipUnless(
        importlib.util.find_spec("qdrant_client"),
        "qdrant-client nao esta instalado",
    )
    def test_indexa_documento_no_qdrant_com_payload_padrao(self):
        qdrant_client = FakeQdrantClient()
        helper = VectorDatabaseHelper(
            collection_name="documentos_teste",
            embedding_model=FakeEmbeddingModel(),
            qdrant_client=qdrant_client,
            vector_size=3,
        )
        documento = DocumentoRAG(
            id="politica_reembolso",
            text="O cliente pode pedir reembolso em ate 7 dias.",
            metadados={"categoria": "financeiro"},
        )

        helper.indexar_documento(documento)

        ponto = qdrant_client.upsert_kwargs["points"][0]
        self.assertEqual(qdrant_client.upsert_kwargs["collection_name"], "documentos_teste")
        self.assertEqual(ponto.vector, [0.1, 0.2, 0.3])
        self.assertEqual(ponto.payload["documento_id"], "politica_reembolso")
        self.assertEqual(ponto.payload["metadados"]["categoria"], "financeiro")


class QdrantVectorStoreTest(unittest.TestCase):
    @unittest.skipUnless(
        importlib.util.find_spec("qdrant_client"),
        "qdrant-client nao esta instalado",
    )
    def test_upsert_documentos_salva_pontos_no_qdrant(self):
        qdrant_client = FakeQdrantClient()
        vector_store = QdrantVectorStore(
            collection_name="documentos_teste",
            qdrant_client=qdrant_client,
            vector_size=3,
        )
        documento = DocumentoRAG(
            id="politica_reembolso",
            text="O cliente pode pedir reembolso em ate 7 dias.",
            metadados={"categoria": "financeiro"},
        )

        vector_store.upsert_documentos(
            documentos=[documento],
            embeddings=[[0.1, 0.2, 0.3]],
        )

        ponto = qdrant_client.upsert_kwargs["points"][0]
        self.assertEqual(qdrant_client.upsert_kwargs["collection_name"], "documentos_teste")
        self.assertEqual(ponto.vector, [0.1, 0.2, 0.3])
        self.assertEqual(ponto.payload["documento_id"], "politica_reembolso")
        self.assertEqual(ponto.payload["text"], "O cliente pode pedir reembolso em ate 7 dias.")

    def test_buscar_por_embedding_converte_resposta_em_documentos(self):
        qdrant_client = FakeQdrantClient()
        vector_store = QdrantVectorStore(
            collection_name="documentos_teste",
            qdrant_client=qdrant_client,
            vector_size=3,
        )

        documentos = vector_store.buscar_por_embedding(
            embedding_query=[0.1, 0.2, 0.3],
            top_k=1,
        )

        self.assertEqual(documentos[0].id, "politica_reembolso")
        self.assertEqual(documentos[0].text, "O cliente pode pedir reembolso em ate 7 dias.")
        self.assertEqual(documentos[0].score, 0.98)
        self.assertEqual(qdrant_client.query_kwargs["query"], [0.1, 0.2, 0.3])
        self.assertEqual(qdrant_client.query_kwargs["limit"], 1)


class DocumentIndexerTest(unittest.TestCase):
    def test_indexar_documentos_gera_embeddings_e_delega_para_vector_store(self):
        vector_store = FakeVectorStore()
        indexer = DocumentIndexer(
            vector_store=vector_store,
            embedding_model=FakeEmbeddingModel(),
        )
        documento = DocumentoRAG(
            id="doc-1",
            text="Texto para indexar.",
            metadados={"fonte": "teste"},
        )

        indexer.indexar_documentos([documento])

        self.assertEqual(vector_store.upsert_documentos_kwargs["documentos"], [documento])
        self.assertEqual(vector_store.upsert_documentos_kwargs["embeddings"], [[0.1, 0.2, 0.3]])

    def test_indexar_documentos_rejeita_lista_vazia(self):
        indexer = DocumentIndexer(
            vector_store=FakeVectorStore(),
            embedding_model=FakeEmbeddingModel(),
        )

        with self.assertRaisesRegex(ValueError, "não pode ser vazia"):
            indexer.indexar_documentos([])


class DocumentRetrieverTest(unittest.TestCase):
    def test_buscar_documentos_relevantes_gera_embedding_e_delega_para_vector_store(self):
        vector_store = FakeVectorStore()
        retriever = DocumentRetriever(
            vector_store=vector_store,
            embedding_model=FakeEmbeddingModel(),
        )

        documentos = retriever.buscar_documentos_relevantes(
            query_usuario="Como funciona reembolso?",
            top_k=2,
            filtro={"categoria": "financeiro"},
        )

        self.assertEqual(vector_store.buscar_por_embedding_kwargs["embedding_query"], [0.1, 0.2, 0.3])
        self.assertEqual(vector_store.buscar_por_embedding_kwargs["top_k"], 2)
        self.assertEqual(vector_store.buscar_por_embedding_kwargs["filtro"], {"categoria": "financeiro"})
        self.assertEqual(documentos[0].text, "O cliente pode pedir reembolso em ate 7 dias.")

    def test_buscar_contexto_relevante_retorna_apenas_textos(self):
        retriever = DocumentRetriever(
            vector_store=FakeVectorStore(),
            embedding_model=FakeEmbeddingModel(),
        )

        contexto = retriever.buscar_contexto_relevante("Como funciona reembolso?")

        self.assertEqual(contexto, ["O cliente pode pedir reembolso em ate 7 dias."])


if __name__ == "__main__":
    unittest.main()
