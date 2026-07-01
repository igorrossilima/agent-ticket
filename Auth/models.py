from pydantic import BaseModel, Field


class UsuarioAutenticado(BaseModel):
    usuario_id: str = Field(min_length=1)
    token: str = Field(min_length=1)
