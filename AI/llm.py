import os
from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def gerar_resposta(self, prompt_sistema: str, prompt_usuario: str) -> str:
        pass


class OpenAIModel(BaseLLM):
    def __init__(self):
        from openai import OpenAI

        self.client = OpenAI()

    def gerar_resposta(self, prompt_sistema: str, prompt_usuario: str) -> str:
        response = self.client.responses.create(
            model="gpt-4o-mini",
            instructions=prompt_sistema,
            input=prompt_usuario,
        )
        print("[Log] Chamando OpenAI...")
        return f"[OpenAI]\n {response.output_text}"


class GeminiModel(BaseLLM):
    def gerar_resposta(self, prompt_sistema: str, prompt_usuario: str) -> str:
        print("[Log] Chamando Gemini...")
        return f"[Gemini] Resposta baseada em:\n {prompt_usuario}"


class DeepseekModel(BaseLLM):
    def __init__(self):
        from openai import OpenAI

        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        )
        self.modelo = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    def gerar_resposta(self, prompt_sistema: str, prompt_usuario: str) -> str:
        response = self.client.chat.completions.create(
            model=self.modelo,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario},
            ],
        )
        print("[Log] Chamando DeepseekModel...")
        return f"[Deepseek]\n {response.choices[0].message.content}"


class LLMFactory:
    @staticmethod
    def criar_modelo(provedor_ia: str) -> BaseLLM:
        if provedor_ia.lower() == "gemini":
            return GeminiModel()

        if provedor_ia.lower() == "deepseek":
            return DeepseekModel()

        if provedor_ia.lower() == "openai":
            return OpenAIModel()

        raise ValueError(f"Provedor não surportado:/n{provedor_ia}")
