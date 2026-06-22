from pydantic import BaseModel

class DocumentoRAG(BaseModel):
    id: str
    text: str # dados que serão transformados atravez do embeddings
    metadados: dict # forma de criar uma etiqueta referente a cada dado, usado para filtro