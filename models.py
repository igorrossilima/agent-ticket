import os
from abc import ABC, abstractmethod
from typing import List, Optional

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

#cria uma classe abstrata para ser usada como modelo para que outras classes herdem ela
class BaseLLM(ABC):
    @abstractmethod # diz que qualquer classe que implementar BaseLLM tera que seguir essa estrutura abaixo
    def gerar_resposta(self, prompt_sistema: str, prompt_usuario: str) -> str:
        pass


class BaseEmbeddingModel(ABC):
    @abstractmethod
    def gerar_embedding(self, texto: str) -> List[float]:
        pass

    def gerar_embeddings(self, textos: List[str]) -> List[List[float]]:
        return [self.gerar_embedding(texto) for texto in textos]


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


class OpenAIEmbeddingModel(BaseEmbeddingModel):
    def __init__(self, modelo: Optional[str] = None, dimensions: Optional[int] = None):
        from openai import OpenAI

        self.client = OpenAI()
        self.modelo = modelo or os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self.dimensions = self._resolver_dimensions(dimensions)

    def gerar_embedding(self, texto: str) -> List[float]:
        if not texto or not texto.strip():
            raise ValueError("O texto para embedding não pode ser vazio.")

        return self.gerar_embeddings([texto.strip()])[0]

    def gerar_embeddings(self, textos: List[str]) -> List[List[float]]:
        textos_limpos = []

        for texto in textos:
            if not texto or not texto.strip():
                raise ValueError("Os textos para embedding não podem conter valores vazios.")

            textos_limpos.append(texto.strip())

        if not textos_limpos:
            raise ValueError("A lista de textos para embedding não pode ser vazia.")

        parametros = {
            "model": self.modelo,
            "input": textos_limpos,
        }

        if self.dimensions:
            parametros["dimensions"] = self.dimensions

        response = self.client.embeddings.create(**parametros)
        print("[Log] Gerando embeddings com OpenAI...")

        dados_ordenados = sorted(response.data, key=lambda item: item.index)
        return [item.embedding for item in dados_ordenados]

    @staticmethod
    def _resolver_dimensions(dimensions: Optional[int]) -> Optional[int]:
        valor = dimensions if dimensions is not None else os.getenv("OPENAI_EMBEDDING_DIMENSIONS")

        if valor in (None, ""):
            return None

        return int(valor)


class GeminiModel(BaseLLM): # puxando a classe da herança como parametro
    def gerar_resposta(self, prompt_sistema: str, prompt_usuario: str) -> str:
        print("[Log] Chamando Gemini...") # mostra que o Gemini foi acionado
        return f"[Gemini] Resposta baseada em:\n {prompt_usuario}" # mock mostrando que a resposta do Gemini foi baseada no prompt do usuario
    
class DeepseekModel(BaseLLM):
    def gerar_resposta(self, prompt_sistema: str, prompt_usuario: str) -> str:
        print("[Log] Chamando DeepseekModel...")
        return f"[Deepseek] Resposta baseada em:\n {prompt_usuario}"
    
class LLMFactory: # define qual será a classe que irá trabalhar
    @staticmethod # permite chamar a classe sem antes precisar instanciar ela em uma variavel
    def criar_modelo(provedor_ia: str) -> BaseLLM: # recebe um modelo que será usado em string e retorna em um formato BaseLLM
        if provedor_ia.lower() == "gemini":
            return GeminiModel()
        
        if provedor_ia.lower() == "deepseek":
            return DeepseekModel()
        
        if provedor_ia.lower() == "openai":
            return OpenAIModel()
        
        raise ValueError(f"Provedor não surportado:/n{provedor_ia}")


class EmbeddingFactory:
    @staticmethod
    def criar_modelo(provedor_ia: str = "openai") -> BaseEmbeddingModel:
        if provedor_ia.lower() == "openai":
            return OpenAIEmbeddingModel()

        raise ValueError(f"Provedor de embedding não suportado:/n{provedor_ia}")
