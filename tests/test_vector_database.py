import importlib.util
import unittest

from Database.structure import DocumentoRAG
from Database.utils import VectorDatabaseHelper
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


if __name__ == "__main__":
    unittest.main()
