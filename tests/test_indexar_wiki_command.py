import unittest

from RAG.commands.indexar_wiki import indexar_wiki
from RAG.structure import DocumentoRAG


class FakeVectorDatabaseHelper:
    collection_name = "documentos_teste"

    def __init__(self):
        self.indexar_markdown_kwargs = None

    def indexar_markdown(self, **kwargs):
        self.indexar_markdown_kwargs = kwargs

        return [
            DocumentoRAG(
                id="wiki-yuv-chunk-1",
                text="Conteudo da wiki.",
                metadados=kwargs["metadados"],
            )
        ]


class IndexarWikiCommandTest(unittest.TestCase):
    def test_indexar_wiki_usa_helper_existente_para_indexar_markdown(self):
        helper = FakeVectorDatabaseHelper()

        resultado = indexar_wiki(
            caminho_arquivo="RAG/data/wiki_yuv_para_chunking_interno.md",
            documento_id="wiki-yuv",
            helper=helper,
        )

        self.assertEqual(resultado.documento_id, "wiki-yuv")
        self.assertEqual(resultado.collection_name, "documentos_teste")
        self.assertEqual(resultado.chunk_total, 1)
        self.assertEqual(
            helper.indexar_markdown_kwargs["caminho_arquivo"],
            "RAG/data/wiki_yuv_para_chunking_interno.md",
        )
        self.assertEqual(
            helper.indexar_markdown_kwargs["documento_id"],
            "wiki-yuv",
        )
        self.assertEqual(
            helper.indexar_markdown_kwargs["metadados"],
            {"tipo": "wiki_yuv"},
        )


if __name__ == "__main__":
    unittest.main()
