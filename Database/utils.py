from typing import List

class VectorDatabaseHelper:
    def __init__(self, db_connection_string: str):
        self.connection = db_connection_string

    def buscar_contexto_relevante(self, query_usuario: str, top_k: int = 3) -> List[str]:
        print(f"[Log DB] Buscando contexto para: {query_usuario}")

        documentos = [
            "Documento 1: Docker ajuda a empacotar aplicações.",
            "Documento 2: Bancos vetoriais são usados em sistemas RAG.",
            "Documento 3: Separação de responsabilidades melhora manutenção.",
        ]

        return documentos[:top_k]