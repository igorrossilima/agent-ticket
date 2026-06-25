import unittest

from Database.chunkers import Chunking, RecursiveChunker, SemanticChunker
from models import BaseEmbeddingModel


class FakeEmbeddingModel(BaseEmbeddingModel):
    def gerar_embedding(self, texto):
        mapa = {
            "Assinatura foi cobrada duas vezes.": [1.0, 0.0],
            "Cliente pediu estorno.": [1.0, 0.0],
            "Senha precisa ser redefinida.": [0.0, 1.0],
        }

        return mapa[texto]


class ChunkingTest(unittest.TestCase):
    def test_recursive_chunker_divide_texto_em_chunks_menores(self):
        chunker = RecursiveChunker(tamanho_chunk=25, sobreposicao=0)

        chunks = chunker.gerar_chunks(
            "Primeiro paragrafo com texto.\n\nSegundo paragrafo com outro texto."
        )

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 25 for chunk in chunks))

    def test_chunking_gera_documentos_rag_com_metadados_de_chunk(self):
        chunking = Chunking(RecursiveChunker(tamanho_chunk=20, sobreposicao=0))

        documentos = chunking.gerar_documentos(
            texto="Parte um. Parte dois. Parte tres.",
            documento_id="manual-suporte",
            metadados={"fonte": "manual"},
        )

        self.assertGreater(len(documentos), 1)
        self.assertEqual(documentos[0].id, "manual-suporte-chunk-1")
        self.assertEqual(documentos[0].metadados["fonte"], "manual")
        self.assertEqual(documentos[0].metadados["documento_origem_id"], "manual-suporte")
        self.assertEqual(documentos[0].metadados["chunk_indice"], 0)
        self.assertEqual(documentos[0].metadados["chunk_total"], len(documentos))

    def test_semantic_chunker_agrupa_sentencas_por_similaridade(self):
        chunker = SemanticChunker(
            embedding_model=FakeEmbeddingModel(),
            tamanho_chunk=100,
            limite_similaridade=0.9,
        )

        chunks = chunker.gerar_chunks(
            "Assinatura foi cobrada duas vezes. Cliente pediu estorno. "
            "Senha precisa ser redefinida."
        )

        self.assertEqual(
            chunks,
            [
                "Assinatura foi cobrada duas vezes. Cliente pediu estorno.",
                "Senha precisa ser redefinida.",
            ],
        )


if __name__ == "__main__":
    unittest.main()
