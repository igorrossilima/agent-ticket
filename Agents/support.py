import json
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Agents.base import Agent


NOME_AGENTE_SUPORTE = "agente_suporte"


class SupportAgent(Agent):
    def __init__(self, provedor_ia: str = "openai"):
        super().__init__(
            nome_agente=NOME_AGENTE_SUPORTE,
            provedor_ia=provedor_ia,
        )

    def executar(
        self,
        mensagem_usuario: str,
        contexto_wiki: str,
        classificacao: Dict[str, Any],
        historico_atendimento: str | None = None,
    ) -> str:
        if not mensagem_usuario or not mensagem_usuario.strip():
            raise ValueError("A mensagem do usuário não pode ser vazia.")

        classificacao = classificacao or {}
        contexto_wiki = contexto_wiki.strip() if contexto_wiki else ""
        historico_atendimento = historico_atendimento.strip() if historico_atendimento else ""

        if not contexto_wiki:
            contexto_wiki = "Nenhum contexto relevante foi encontrado na base da wiki."

        if not historico_atendimento:
            historico_atendimento = "Nenhum histórico anterior neste ticket."

        return self.executar_prompt(
            mensagem_usuario=mensagem_usuario.strip(),
            contexto_wiki=contexto_wiki,
            classificacao=json.dumps(classificacao, ensure_ascii=False),
            historico_atendimento=historico_atendimento,
        )
