"""Comando manual para inspecionar os chunks retornados pelo retriever."""

import argparse
from typing import Optional, Sequence

from RAG.utils import VectorDatabaseHelper


QUERY_PADRAO = "Como consulto eventos de excesso de velocidade ?"
TOP_K_PADRAO = 5
LIMITE_TEXTO_PADRAO = 1200


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Busca chunks relevantes no Qdrant usando o retriever do RAG.",
    )
    parser.add_argument(
        "query",
        nargs="?",
        default=QUERY_PADRAO,
        help=f"Texto da busca. Padrao: '{QUERY_PADRAO}'.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=TOP_K_PADRAO,
        help=f"Quantidade de chunks retornados. Padrao: {TOP_K_PADRAO}.",
    )
    parser.add_argument(
        "--collection",
        default=None,
        help="Nome da collection no Qdrant. Se omitido, usa QDRANT_COLLECTION.",
    )
    parser.add_argument(
        "--limite-texto",
        type=int,
        default=LIMITE_TEXTO_PADRAO,
        help=f"Limite de caracteres impressos por chunk. Padrao: {LIMITE_TEXTO_PADRAO}.",
    )

    return parser


def _formatar_texto(texto: str, limite_texto: int) -> str:
    if limite_texto <= 0 or len(texto) <= limite_texto:
        return texto

    return f"{texto[:limite_texto].rstrip()}..."


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = criar_parser().parse_args(argv)
    helper = VectorDatabaseHelper(collection_name=args.collection)
    documentos = helper.buscar_documentos_relevantes(
        query_usuario=args.query,
        top_k=args.top_k,
    )

    print(f"Query: {args.query}")
    print(f"Collection: {helper.collection_name}")
    print(f"Top K solicitado: {args.top_k}")
    print(f"Resultados retornados: {len(documentos)}")

    if not documentos:
        print("\nNenhum chunk encontrado.")
        return

    for indice, documento in enumerate(documentos, start=1):
        print("\n" + "=" * 80)
        print(f"Resultado #{indice}")
        print(f"ID: {documento.id}")
        print(f"Score: {documento.score}")
        print(f"Metadados: {documento.metadados}")
        print("Texto:")
        print(_formatar_texto(documento.text, args.limite_texto))


if __name__ == "__main__":
    main()
