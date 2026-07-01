from pydantic import BaseModel, Field

# passo 7
class UsuarioAutenticado(BaseModel):
    usuario_id: str = Field(min_length=1)
    token: str = Field(min_length=1)
