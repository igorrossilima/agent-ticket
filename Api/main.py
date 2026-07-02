from typing import Callable, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from Auth.models import UsuarioAutenticado
from Auth.token_service import TokenInvalidoError, TokenService
from Sessions.models import SessaoConversa
from Sessions.repository import InMemorySessionRepository
from Sessions.service import SessionService
from Tickets.routes import router as tickets_router
from Workers.main import executar_fluxo_suporte


FluxoSuporteExecutor = Callable[..., str]
_token_service = TokenService()
_session_repository = InMemorySessionRepository() # busca na memoria o repositorio com o passo 10
_session_service = SessionService(repository=_session_repository) # pega a o usuario 9 com a sessao do reposito

app = FastAPI(
    title="API Agente de Suporte YUV",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    mensagem: str
    top_k: int = Field(default=3, ge=1, le=10)
    provedor_ia: str = "openai"


class ChatResponse(BaseModel):
    resposta: str
    session_id: str
    top_k: int
    provedor_ia: str


async def obter_executor_fluxo() -> FluxoSuporteExecutor:
    return executar_fluxo_suporte

# passo 5
async def obter_token_service() -> TokenService:
    return _token_service # retorna um token que foi buscado ou criado no passo 6

# passo 8
async def obter_session_service() -> SessionService:
    return _session_service # busca sessao do servico na variavel fora das funções

# passo 3
async def obter_usuario_autenticado(
    authorization: Optional[str] = Header(default=None),
    token_service: TokenService = Depends(obter_token_service),# chama a função do passo 5
) -> UsuarioAutenticado:
    token = extrair_token_bearer(authorization) # chama o passo 4

    try:
        return token_service.identificar_usuario(token)
    except TokenInvalidoError as erro: # se o passo 4 nao retornar um token valido
        raise HTTPException(
            status_code=401,
            detail=str(erro),
            headers={"WWW-Authenticate": "Bearer"},
        ) from erro

# passo 2
async def obter_sessao_conversa(
    usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado), # chama o passo 3
    session_service: SessionService = Depends(obter_session_service), # chama o passo 8
) -> SessaoConversa:
    return session_service.obter_ou_criar_sessao(usuario) # retorna a sessao ou cria com base no usuario

# passo 4
def extrair_token_bearer(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Token de autenticação não informado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    esquema, separador, token = authorization.partition(" ")

    if separador != " " or esquema.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=401,
            detail="Header Authorization deve usar o formato Bearer <token>.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

# passo 1 e 13
@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    sessao: SessaoConversa = Depends(obter_sessao_conversa), # aqui retorna todo o processo do passo 12
    executor_fluxo: FluxoSuporteExecutor = Depends(obter_executor_fluxo), # aqui amarra o fluxo do Workers para ser chamado depois
) -> ChatResponse:
    mensagem = request.mensagem.strip() if request.mensagem else ""

    if not mensagem:
        raise HTTPException(
            status_code=400,
            detail="A mensagem do usuário não pode ser vazia.",
        )

    provedor_ia = request.provedor_ia.strip() if request.provedor_ia else "openai"
    provedor_ia = provedor_ia or "openai"

    try: # aqui é pausado o fluxo da API e iniciado o fluxo do Worker
        resposta = await run_in_threadpool(
            executor_fluxo,
            mensagem_usuario=mensagem,
            provedor_ia=provedor_ia,
            top_k=request.top_k,
        ) # aqui retorna para o fluxo da API
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar a mensagem.",
        ) from erro

    return ChatResponse(
        resposta=resposta,
        session_id=sessao.session_id,
        top_k=request.top_k,
        provedor_ia=provedor_ia,
    )


app.include_router(
    tickets_router,
    dependencies=[Depends(obter_usuario_autenticado)],
)
