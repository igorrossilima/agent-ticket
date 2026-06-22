from abc import ABC, abstractmethod

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
