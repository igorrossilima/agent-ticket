import sys
from pathlib import Path
from typing import Any, Dict, Union

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Agents.base import Agent
from Shared.constants import DEFAULT_TICKET_CATEGORY, TICKET_CATEGORIES


NOME_AGENTE_CLASSIFICADOR = "agente_classificador"

class Classifier(Agent):
    def __init__(self, provedor_ia: str = "openai"):
        super().__init__(
            nome_agente=NOME_AGENTE_CLASSIFICADOR,
            provedor_ia=provedor_ia,
        )

    @staticmethod
    def normalizar_classificacao(classificacao: Dict[str, Any]) -> Dict[str, Any]:
        categoria = str(classificacao.get("categoria") or DEFAULT_TICKET_CATEGORY).strip()
        if categoria not in TICKET_CATEGORIES:
            categoria = DEFAULT_TICKET_CATEGORY

        classificacao["categoria"] = categoria
        classificacao["confianca"] = Classifier._normalizar_confianca(classificacao.get("confianca", 0.0))
        classificacao["intencao"] = (
            classificacao.get("intencao") or "nao_identificada"
        )
        classificacao["termos_busca"] = classificacao.get("termos_busca") or []
        classificacao["justificativa"] = (
            classificacao.get("justificativa")
            or "Classificação sem justificativa."
        )

        return classificacao

    @staticmethod
    def _normalizar_confianca(value: Any) -> float:
        try:
            confianca = float(value)
        except (TypeError, ValueError):
            return 0.0

        if confianca < 0:
            return 0.0

        if confianca > 1:
            return 1.0

        return confianca

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

        classificacao = self.extrair_json_resposta(resposta)

        return self.normalizar_classificacao(classificacao)


if __name__ == "__main__":
    ticket_teste = "Quero cancelar minha assinatura porque fui cobrado duas vezes."
    classificacao = Classifier(provedor_ia="openai").executar(ticket_teste)
    print(classificacao)
