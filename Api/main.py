from typing import Callable, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from Auth.models import UsuarioAutenticado
from Auth.token_service import TokenInvalidoError, TokenService
from Sessions.models import SessaoConversa
from Sessions.repository import InMemorySessionRepository
from Sessions.service import SessionService
from Workers.main import executar_fluxo_suporte


FluxoSuporteExecutor = Callable[..., str]
_token_service = TokenService()
_session_repository = InMemorySessionRepository()
_session_service = SessionService(repository=_session_repository)

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


async def obter_token_service() -> TokenService:
    return _token_service


async def obter_session_service() -> SessionService:
    return _session_service


async def obter_usuario_autenticado(
    authorization: Optional[str] = Header(default=None),
    token_service: TokenService = Depends(obter_token_service),
) -> UsuarioAutenticado:
    token = extrair_token_bearer(authorization)

    try:
        return token_service.identificar_usuario(token)
    except TokenInvalidoError as erro:
        raise HTTPException(
            status_code=401,
            detail=str(erro),
            headers={"WWW-Authenticate": "Bearer"},
        ) from erro


async def obter_sessao_conversa(
    usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado),
    session_service: SessionService = Depends(obter_session_service),
) -> SessaoConversa:
    return session_service.obter_ou_criar_sessao(usuario)


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


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    sessao: SessaoConversa = Depends(obter_sessao_conversa),
    executor_fluxo: FluxoSuporteExecutor = Depends(obter_executor_fluxo),
) -> ChatResponse:
    mensagem = request.mensagem.strip() if request.mensagem else ""

    if not mensagem:
        raise HTTPException(
            status_code=400,
            detail="A mensagem do usuário não pode ser vazia.",
        )

    provedor_ia = request.provedor_ia.strip() if request.provedor_ia else "openai"
    provedor_ia = provedor_ia or "openai"

    try:
        resposta = executor_fluxo(
            mensagem_usuario=mensagem,
            provedor_ia=provedor_ia,
            top_k=request.top_k,
        )
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
