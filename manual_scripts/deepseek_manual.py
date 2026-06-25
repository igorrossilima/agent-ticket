import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models import DeepseekModel


def main():
    modelo = DeepseekModel()

    resposta = modelo.gerar_resposta(
        prompt_sistema="Responda apenas com a palavra OK.",
        prompt_usuario="Teste de conexao.",
    )

    print(resposta)


if __name__ == "__main__":
    main()
