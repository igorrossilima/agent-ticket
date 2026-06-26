import unittest

from Database.structure import DocumentoRAG
from Workers.main import (
    executar_fluxo_suporte,
    formatar_contexto_documentos,
    montar_query_busca,
)


class FakeClassifier:
    def __init__(self):
        self.mensagem = None

    def executar(self, mensagem):
        self.mensagem = mensagem
        return {
            "categoria": "suporte",
            "confianca": 0.9,
            "justificativa": "Cliente perguntou sobre eventos de velocidade.",
            "intencao": "consultar_eventos",
            "termos_busca": ["eventos", "excesso de velocidade"],
        }


class FakeDatabase:
    def __init__(self):
        self.query_usuario = None
        self.top_k = None

    def buscar_documentos_relevantes(self, query_usuario, top_k=3):
        self.query_usuario = query_usuario
        self.top_k = top_k
        return [
            DocumentoRAG(
                id="teste-wiki-chunk-1",
                text="O sistema registra eventos de excesso de velocidade.",
                metadados={"documento_origem_id": "teste-wiki"},
                score=0.98,
            )
        ]


class FakeSupportAgent:
    def __init__(self):
        self.mensagem_usuario = None
        self.contexto_wiki = None
        self.classificacao = None

    def executar(self, mensagem_usuario, contexto_wiki, classificacao):
        self.mensagem_usuario = mensagem_usuario
        self.contexto_wiki = contexto_wiki
        self.classificacao = classificacao
        return "Resposta final ao cliente."


class WorkerSupportFlowTest(unittest.TestCase):
    def test_montar_query_busca_com_classificacao_completa(self):
        query = montar_query_busca(
            mensagem_usuario="Como vejo eventos de velocidade?",
            classificacao={
                "categoria": "suporte",
                "justificativa": "Cliente perguntou sobre eventos.",
                "intencao": "consultar_eventos",
                "termos_busca": ["eventos", "velocidade"],
            },
        )

        self.assertIn("Como vejo eventos de velocidade?", query)
        self.assertIn("suporte", query)
        self.assertIn("Cliente perguntou sobre eventos.", query)
        self.assertIn("consultar_eventos", query)
        self.assertIn("eventos", query)
        self.assertIn("velocidade", query)

    def test_montar_query_busca_com_classificacao_parcial_ou_vazia(self):
        query_parcial = montar_query_busca(
            mensagem_usuario="Como vejo eventos?",
            classificacao={"categoria": "suporte"},
        )
        query_vazia = montar_query_busca(
            mensagem_usuario="Como vejo eventos?",
            classificacao={},
        )

        self.assertEqual(query_parcial, "Como vejo eventos? suporte")
        self.assertEqual(query_vazia, "Como vejo eventos?")

    def test_montar_query_busca_rejeita_mensagem_vazia(self):
        with self.assertRaisesRegex(ValueError, "não pode ser vazia"):
            montar_query_busca("   ", {})

    def test_formatar_contexto_documentos(self):
        contexto = formatar_contexto_documentos(
            [
                DocumentoRAG(
                    id="doc-1",
                    text="Texto do chunk.",
                    metadados={"documento_origem_id": "wiki-yuv"},
                    score=0.98765,
                )
            ]
        )

        self.assertIn("[Documento 1 | score=0.9877 | origem=wiki-yuv]", contexto)
        self.assertIn("Texto do chunk.", contexto)

    def test_formatar_contexto_documentos_sem_resultados(self):
        self.assertEqual(formatar_contexto_documentos([]), "")

    def test_executar_fluxo_suporte_orquestra_classificacao_busca_e_resposta(self):
        classificador = FakeClassifier()
        db = FakeDatabase()
        agente_suporte = FakeSupportAgent()

        resposta = executar_fluxo_suporte(
            mensagem_usuario="Como vejo eventos de velocidade?",
            provedor_ia="fake",
            classificador=classificador,
            db=db,
            agente_suporte=agente_suporte,
            top_k=5,
        )

        self.assertEqual(resposta, "Resposta final ao cliente.")
        self.assertEqual(classificador.mensagem, "Como vejo eventos de velocidade?")
        self.assertEqual(db.top_k, 5)
        self.assertIn("excesso de velocidade", db.query_usuario)
        self.assertIn("O sistema registra eventos", agente_suporte.contexto_wiki)
        self.assertEqual(agente_suporte.classificacao["categoria"], "suporte")


if __name__ == "__main__":
    unittest.main()
