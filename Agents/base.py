import json
import os
import sys
from typing import Any, Dict

import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import LLMFactory

class Agent:
    def __init__(self, nome_agente: str, provedor_ia: str = "openai"):
        self.nome_agente = nome_agente
        self.provedor_ia = provedor_ia
        self.caminho_prompt = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../Schemas/prompt_agente.yaml")
        )
        self.prompt = self.carregar_prompt(self.caminho_prompt, self.nome_agente)
        self.modelo_ia = LLMFactory.criar_modelo(self.provedor_ia)

    @staticmethod
    def carregar_prompt(caminho_arquivo: str, nome_agente: str) -> Dict[str, str]:
        with open(caminho_arquivo, "r", encoding="utf-8") as file:
            schemas = yaml.safe_load(file)

        if not schemas or nome_agente not in schemas:
            raise ValueError(f"Prompt do agente não encontrado: {nome_agente}")

        prompt = schemas[nome_agente]

        if "system" not in prompt or "user" not in prompt:
            raise ValueError(
                f"Prompt do agente {nome_agente} precisa conter as chaves 'system' e 'user'."
            )

        return {
            "system": prompt["system"],
            "user": prompt["user"],
        }

    def executar_prompt(self, **dados_prompt: Any) -> str:
        prompt_usuario = self.prompt["user"].format(**dados_prompt)

        return self.modelo_ia.gerar_resposta(
            prompt_sistema=self.prompt["system"],
            prompt_usuario=prompt_usuario,
        )

    @staticmethod
    def extrair_json_resposta(resposta: str) -> Dict[str, Any]:
        inicio_json = resposta.find("{")
        fim_json = resposta.rfind("}")

        if inicio_json == -1 or fim_json == -1 or fim_json < inicio_json: # valida se encontrou a posição de abertura e fechamento do json
            return {
                "categoria": "outros",
                "confianca": 0.0,
                "justificativa": "A resposta da IA não veio em JSON válido.",
                "resposta_original": resposta,
            }

        conteudo_json = resposta[inicio_json : fim_json + 1]

        try:
            return json.loads(conteudo_json)
        except json.JSONDecodeError:
            return {
                "categoria": "outros",
                "confianca": 0.0,
                "justificativa": "Não foi possível interpretar o JSON retornado pela IA.",
                "resposta_original": resposta,
            }
