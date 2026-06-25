import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
