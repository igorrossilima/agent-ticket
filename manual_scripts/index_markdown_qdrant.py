import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.append(str(Path(__file__).resolve().parent.parent))

from RAG.utils import VectorDatabaseHelper


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Indexa um arquivo Markdown no Qdrant usando embeddings.",
    )
    parser.add_argument("caminho_arquivo", help="Caminho do arquivo .md que sera indexado.")
    parser.add_argument("--documento-id", help="ID base do documento. Se omitido, usa o nome do arquivo.")
    parser.add_argument(
        "--metadado",
        action="append",
        default=[],
        help="Metadado extra no formato chave=valor. Pode ser usado mais de uma vez.",
    )

    return parser


def parse_metadados(valores: List[str]) -> Dict[str, Any]:
    metadados = {}

    for valor in valores:
        if "=" not in valor:
            raise ValueError(f"Metadado invalido, use chave=valor: {valor}")

        chave, conteudo = valor.split("=", 1)
        chave = chave.strip()

        if not chave:
            raise ValueError(f"Metadado invalido, chave vazia: {valor}")

        metadados[chave] = conteudo.strip()

    return metadados


def main() -> None:
    args = criar_parser().parse_args()
    metadados = parse_metadados(args.metadado)

    helper = VectorDatabaseHelper(criar_collection=True)
    documentos = helper.indexar_markdown(
        caminho_arquivo=args.caminho_arquivo,
        documento_id=args.documento_id,
        metadados=metadados,
    )

    print("Indexacao concluida.")
    print(f"Collection: {helper.collection_name}")
    print(f"Chunks indexados: {len(documentos)}")


if __name__ == "__main__":
    main()
