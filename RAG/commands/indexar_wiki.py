"""Comando para indexar a wiki usando a fachada VectorDatabaseHelper."""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Sequence

from RAG.utils import VectorDatabaseHelper


CAMINHO_WIKI_PADRAO = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "wiki_yuv_para_chunking_interno.md"
)
DOCUMENTO_ID_PADRAO = "wiki-yuv"


@dataclass
class ResultadoIndexacaoWiki:
    documento_id: str
    caminho_arquivo: str
    collection_name: str
    chunk_total: int


def indexar_wiki(
    caminho_arquivo: str | Path = CAMINHO_WIKI_PADRAO,
    documento_id: str = DOCUMENTO_ID_PADRAO,
    collection_name: Optional[str] = None,
    helper: Optional[Any] = None,
) -> ResultadoIndexacaoWiki:
    caminho = Path(caminho_arquivo)
    helper = helper or VectorDatabaseHelper(
        collection_name=collection_name,
        criar_collection=True,
    )
    documentos = helper.indexar_markdown(
        caminho_arquivo=str(caminho),
        documento_id=documento_id,
        metadados={
            "tipo": "wiki_yuv",
        },
    )

    return ResultadoIndexacaoWiki(
        documento_id=documento_id,
        caminho_arquivo=str(caminho),
        collection_name=helper.collection_name,
        chunk_total=len(documentos),
    )


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Indexa a wiki da YUV no Qdrant.",
    )
    parser.add_argument(
        "--arquivo",
        default=str(CAMINHO_WIKI_PADRAO),
        help="Caminho do arquivo markdown que sera indexado.",
    )
    parser.add_argument(
        "--documento-id",
        default=DOCUMENTO_ID_PADRAO,
        help="Identificador base usado para gerar os chunks.",
    )
    parser.add_argument(
        "--collection",
        default=None,
        help="Nome da collection no Qdrant. Se omitido, usa QDRANT_COLLECTION.",
    )

    return parser


def main(argv: Optional[Sequence[str]] = None) -> ResultadoIndexacaoWiki:
    args = criar_parser().parse_args(argv)
    resultado = indexar_wiki(
        caminho_arquivo=args.arquivo,
        documento_id=args.documento_id,
        collection_name=args.collection,
    )

    print(
        "Indexacao concluida: "
        f"{resultado.chunk_total} chunks do documento "
        f"'{resultado.documento_id}' na collection "
        f"'{resultado.collection_name}'."
    )

    return resultado


if __name__ == "__main__":
    main()
