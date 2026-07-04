"""Camada de modelos de IA usados por agentes e RAG."""

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()
