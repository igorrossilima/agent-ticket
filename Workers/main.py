import sys
from pathlib import Path
import yaml

sys.path.append(str(Path(__file__).resolve().parent.parent)) # volta uma pagina para importar alguma coisa dentro de outro arquivo

from models import LLMFactory
from Database.utils import VectorDatabaseHelper
from Agents.classifier import executar_classificador_ticket

def carregar_prompt(caminho_arquivo: str, nome_agente: str) -> str: # busca o caminho do prompt e qual o agente que vai trabalhar
    with open(caminho_arquivo, "r", encoding="utf-8") as file: # espera receber o enderenço do arquivo, faz a leitura e consideraça ç e outros
        schemas = yaml.safe_load(file) # salva na variavel schemas a consulta do arquivo yaml

    return schemas[nome_agente]["content"]

def executar_agente_ia(mensagem_usuario: str, provedor_ia: str = "gemini"): # executa o agente de IA buscando a mensagem do usuario e definindo default para gemini o agente
    caminho_prompt = Path(__file__).resolve().parent.parent / "Schemas" / "prompt_agente.yaml"

    prompt_sistema = carregar_prompt(caminho_prompt, "agente_suporte")

    db = VectorDatabaseHelper()
    documentos = db.buscar_contexto_relevante(mensagem_usuario) # Busca na lista fake os 3 documentos mais parecidos com a pergunta do usuário

    contexto_formatado = "\n".join(documentos)

    # gera um prompt que unifica o contexto com a mensagem atual do usuario
    prompt_enriquecido = f"""
    Contexto da Base de Conhecimento:
    {contexto_formatado}

    Pergunta do Usuário:
    {mensagem_usuario}
    """
    
    modelo_ia = LLMFactory.criar_modelo(provedor_ia) # cria um modelo de ia seguindo os parametros da herança

    resposta = modelo_ia.gerar_resposta(
        prompt_sistema=prompt_sistema,
        prompt_usuario=prompt_enriquecido
    )

    return resposta

    
if __name__ == "__main__":
    ticket_teste = "Quero cancelar minha assinatura porque fui cobrado duas vezes."
    classificacao = executar_classificador_ticket(ticket_teste, provedor_ia="openai")
    print(classificacao)
