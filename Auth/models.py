from pydantic import BaseModel, Field

# passo 7
class UsuarioAutenticado(BaseModel):
    usuario_id: str = Field(min_length=1)
    token: str = Field(min_length=1)
    email: str = Field(min_length=1)
    name: str = Field(min_length=1)
    role: str = Field(min_length=1)
