import sys
from pathlib import Path
from typing import Any, Dict, Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Agents.base import Agent


NOME_AGENTE_CLASSIFICADOR = "agente_classificador"

class Classifier(Agent):
    def __init__(self, provedor_ia: str = "openai"):
        super().__init__(
            nome_agente=NOME_AGENTE_CLASSIFICADOR,
            provedor_ia=provedor_ia,
        )

    def executar(
        self,
        ticket: str,
        retornar_json: bool = True,
    ) -> Union[Dict[str, Any], str]:
        if not ticket or not ticket.strip():
            raise ValueError("O texto do ticket não pode ser vazio.")

        resposta = self.executar_prompt(ticket=ticket.strip())

        if not retornar_json:
            return resposta

        return self.extrair_json_resposta(resposta)


if __name__ == "__main__":
    ticket_teste = "Quero cancelar minha assinatura porque fui cobrado duas vezes."
    classificacao = Classifier(provedor_ia="openai").executar(ticket_teste)
    print(classificacao)
