from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

class DocumentoRAG(BaseModel):
    id: str
    text: str # dados que serao transformados atraves dos embeddings
    metadados: Dict[str, Any] = Field(default_factory=dict) # etiquetas usadas para filtros
    embedding: Optional[List[float]] = None
    score: Optional[float] = None
