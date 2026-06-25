import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Database.chunkers import RecursiveChunker
from Database.ingestion import JsonlChunkWriter, MarkdownIngestionService


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera chunks locais em JSONL a partir de um arquivo Markdown.",
    )
    parser.add_argument("caminho_arquivo", help="Caminho do arquivo .md que sera ingerido.")
    parser.add_argument("--documento-id", help="ID do documento. Se omitido, usa o nome do arquivo.")
    parser.add_argument(
        "--output",
        default="outputs/chunks",
        help="Diretorio onde o arquivo JSONL sera salvo.",
    )
    parser.add_argument(
        "--tamanho-chunk",
        type=int,
        default=1000,
        help="Tamanho maximo de cada chunk.",
    )
    parser.add_argument(
        "--sobreposicao",
        type=int,
        default=100,
        help="Quantidade de caracteres de sobreposicao entre chunks.",
    )

    return parser


def main() -> None:
    args = criar_parser().parse_args()
    chunker = RecursiveChunker(
        tamanho_chunk=args.tamanho_chunk,
        sobreposicao=args.sobreposicao,
    )
    service = MarkdownIngestionService(
        writer=JsonlChunkWriter(output_dir=args.output),
        chunker=chunker,
    )
    resultado = service.ingestir(
        caminho_arquivo=args.caminho_arquivo,
        documento_id=args.documento_id,
    )

    print("Ingestion concluido.")
    print(f"Documento: {resultado.documento_id}")
    print(f"Chunks: {resultado.chunk_total}")
    print(f"Arquivo: {resultado.output_path}")


if __name__ == "__main__":
    main()
