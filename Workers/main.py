import sys
from pathlib import Path
from collections.abc import Iterable
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parent.parent)) # volta uma pagina para importar alguma coisa dentro de outro arquivo

from Database.utils import VectorDatabaseHelper
from Database.structure import DocumentoRAG
from Agents.classifier import Classifier
from Agents.support import SupportAgent


def montar_query_busca(mensagem_usuario: str, classificacao: Optional[Dict[str, Any]]) -> str:
    if not mensagem_usuario or not mensagem_usuario.strip():
        raise ValueError("A mensagem do usuário não pode ser vazia.")

    partes = [mensagem_usuario.strip()]
    classificacao = classificacao or {}

    for campo in ("categoria", "intencao", "justificativa"):
        valor = classificacao.get(campo)

        if valor:
            partes.append(str(valor).strip())

    termos_busca = classificacao.get("termos_busca")

    if isinstance(termos_busca, str):
        partes.append(termos_busca.strip())
    elif isinstance(termos_busca, Iterable):
        partes.extend(str(termo).strip() for termo in termos_busca if termo)

    return " ".join(parte for parte in partes if parte)


def formatar_contexto_documentos(documentos: List[DocumentoRAG]) -> str:
    if not documentos:
        return ""

    blocos = []

    for indice, documento in enumerate(documentos, start=1):
        score = f" | score={documento.score:.4f}" if documento.score is not None else ""
        origem = documento.metadados.get("documento_origem_id") or documento.metadados.get("nome_arquivo")
        origem_texto = f" | origem={origem}" if origem else ""
        blocos.append(
            f"[Documento {indice}{score}{origem_texto}]\n{documento.text}"
        )

    return "\n\n".join(blocos)


def executar_fluxo_suporte(
    mensagem_usuario: str,
    provedor_ia: str = "openai",
    classificador: Optional[Classifier] = None,
    db: Optional[VectorDatabaseHelper] = None,
    agente_suporte: Optional[SupportAgent] = None,
    top_k: int = 3,
) -> str:
    if not mensagem_usuario or not mensagem_usuario.strip():
        raise ValueError("A mensagem do usuário não pode ser vazia.")

    classificador = classificador or Classifier(provedor_ia=provedor_ia)
    db = db or VectorDatabaseHelper()
    agente_suporte = agente_suporte or SupportAgent(provedor_ia=provedor_ia)

    classificacao = classificador.executar(mensagem_usuario)
    query_busca = montar_query_busca(
        mensagem_usuario=mensagem_usuario,
        classificacao=classificacao,
    )
    documentos = db.buscar_documentos_relevantes(
        query_usuario=query_busca,
        top_k=top_k,
    )
    contexto_wiki = formatar_contexto_documentos(documentos)

    return agente_suporte.executar(
        mensagem_usuario=mensagem_usuario,
        contexto_wiki=contexto_wiki,
        classificacao=classificacao,
    )


if __name__ == "__main__":
    mensagem_teste = "Como faço para consultar eventos de excesso de velocidade?"
    resposta = executar_fluxo_suporte(mensagem_teste, provedor_ia="openai")
    print(resposta)
