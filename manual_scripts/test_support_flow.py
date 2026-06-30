import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Workers.main import executar_fluxo_suporte


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Executa manualmente o fluxo completo de suporte com RAG.",
    )
    parser.add_argument("mensagem", help="Mensagem do usuario/cliente.")
    parser.add_argument(
        "--provedor-ia",
        default="openai",
        help="Provedor de IA usado pelos agentes. Padrao: openai.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Quantidade de chunks retornados do Qdrant. Padrao: 3.",
    )

    return parser


def main() -> None:
    args = criar_parser().parse_args()
    resposta = executar_fluxo_suporte(
        mensagem_usuario=args.mensagem,
        provedor_ia=args.provedor_ia,
        top_k=args.top_k,
    )

    print(resposta)


if __name__ == "__main__":
    main()
