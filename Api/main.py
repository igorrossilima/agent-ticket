from typing import Callable, Optional
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from Auth.models import UsuarioAutenticado
from Auth.routes import router as auth_router
from Auth.token_service import TokenInvalidoError, TokenService
from Customers.routes import router as customers_router
from Integrations.Chatwoot.routes import router as chatwoot_router
from Postgres.session import obter_sessao_db
from Tickets.chat_helpers import (
    extrair_classificacao_fluxo,
    extrair_documentos_fluxo,
    extrair_resposta_fluxo,
    formatar_historico_atendimento,
    montar_metadata_mensagem_ia,
    resposta_requer_handoff_humano,
)
from Tickets.routes import router as tickets_router
from Tickets.schemas import TicketCreate, TicketMessageCreate
from Tickets.service import (
    CustomerNaoEncontradoError,
    TicketNaoEncontradoError,
    TicketService,
    TicketServiceError,
    UserNaoEncontradoError,
    ValorTicketInvalidoError,
)
from Workers.main import executar_fluxo_suporte_detalhado


FluxoSuporteExecutor = Callable[..., object]
HISTORICO_CHAT_LIMITE = 10
_token_service = TokenService()

app = FastAPI(
    title="API Agente de Suporte YUV",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    mensagem: str
    customer_id: UUID
    ticket_id: UUID | None = None
    title: str | None = Field(default=None, max_length=255)
    top_k: int = Field(default=3, ge=1, le=10)
    provedor_ia: str = "openai"


class ChatResponse(BaseModel):
    resposta: str
    ticket_id: UUID
    top_k: int
    provedor_ia: str


async def obter_executor_fluxo() -> FluxoSuporteExecutor:
    return executar_fluxo_suporte_detalhado

# passo 5
async def obter_token_service() -> TokenService:
    return _token_service # retorna um token que foi buscado ou criado no passo 6

# passo 3
async def obter_usuario_autenticado(
    authorization: Optional[str] = Header(default=None),
    token_service: TokenService = Depends(obter_token_service),# chama a função do passo 5
    db_session: Session = Depends(obter_sessao_db),
) -> UsuarioAutenticado:
    token = extrair_token_bearer(authorization) # chama o passo 4

    try:
        return token_service.identificar_usuario(token, db_session)
    except TokenInvalidoError as erro: # se o passo 4 nao retornar um token valido
        raise HTTPException(
            status_code=401,
            detail=str(erro),
            headers={"WWW-Authenticate": "Bearer"},
        ) from erro

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
    _usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado),
    executor_fluxo: FluxoSuporteExecutor = Depends(obter_executor_fluxo), # aqui amarra o fluxo do Workers para ser chamado depois
    db_session: Session = Depends(obter_sessao_db),
) -> ChatResponse:
    mensagem = request.mensagem.strip() if request.mensagem else ""

    if not mensagem:
        raise HTTPException(
            status_code=400,
            detail="A mensagem do usuário não pode ser vazia.",
        )

    provedor_ia = request.provedor_ia.strip() if request.provedor_ia else "openai"
    provedor_ia = provedor_ia or "openai"
    ticket_service = TicketService(db_session)

    try:
        ticket = _obter_ou_criar_ticket_chat(
            ticket_service=ticket_service,
            request=request,
            mensagem=mensagem,
        )
        historico_atendimento = formatar_historico_atendimento(
            ticket_service.listar_mensagens_ticket(
                ticket.id,
                limit=HISTORICO_CHAT_LIMITE,
            )
        )
        ticket_service.adicionar_mensagem(
            TicketMessageCreate(
                ticket_id=ticket.id,
                sender_type="customer",
                sender_customer_id=request.customer_id,
                body=mensagem,
            )
        )
    except TicketServiceError as erro:
        db_session.rollback()
        raise _converter_erro_ticket_chat(erro) from erro

    try: # aqui é pausado o fluxo da API e iniciado o fluxo do Worker
        resultado_fluxo = await run_in_threadpool(
            executor_fluxo,
            mensagem_usuario=mensagem,
            provedor_ia=provedor_ia,
            top_k=request.top_k,
            historico_atendimento=historico_atendimento,
        ) # aqui retorna para o fluxo da API
        resposta = extrair_resposta_fluxo(resultado_fluxo)
        classificacao = extrair_classificacao_fluxo(resultado_fluxo)
        documentos_rag = extrair_documentos_fluxo(resultado_fluxo)
        requer_humano = resposta_requer_handoff_humano(resposta)
    except ValueError as erro:
        db_session.rollback()
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    except Exception as erro:
        db_session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar a mensagem.",
        ) from erro

    try:
        if classificacao:
            ticket_service.aplicar_classificacao_agente(
                ticket.id,
                classificacao,
                requires_human=requer_humano,
            )

        ticket_service.adicionar_mensagem(
            TicketMessageCreate(
                ticket_id=ticket.id,
                sender_type="ai_agent",
                body=resposta,
                metadata=montar_metadata_mensagem_ia(
                    classificacao=classificacao,
                    documentos_rag=documentos_rag,
                    top_k=request.top_k,
                    provedor_ia=provedor_ia,
                ),
            )
        )
        if requer_humano:
            ticket_service.marcar_handoff_humano(ticket.id)

        db_session.commit()
        db_session.refresh(ticket)
    except TicketServiceError as erro:
        db_session.rollback()
        raise _converter_erro_ticket_chat(erro) from erro

    return ChatResponse(
        resposta=resposta,
        ticket_id=ticket.id,
        top_k=request.top_k,
        provedor_ia=provedor_ia,
    )


def _obter_ou_criar_ticket_chat(
    *,
    ticket_service: TicketService,
    request: ChatRequest,
    mensagem: str,
):
    if request.ticket_id:
        ticket = ticket_service.obter_ticket(request.ticket_id)

        if ticket.customer_id != request.customer_id:
            raise ValorTicketInvalidoError("Cliente informado nao pertence ao ticket.")

        return ticket

    title = request.title.strip() if request.title else ""
    title = title or _gerar_titulo_ticket(mensagem)

    return ticket_service.criar_ticket(
        TicketCreate(
            customer_id=request.customer_id,
            title=title,
            description=mensagem,
            source="api",
        )
    )


def _gerar_titulo_ticket(mensagem: str) -> str:
    titulo = mensagem.strip().replace("\n", " ")

    if len(titulo) <= 80:
        return titulo

    return f"{titulo[:77].rstrip()}..."


def _converter_erro_ticket_chat(erro: TicketServiceError) -> HTTPException:
    if isinstance(erro, (TicketNaoEncontradoError, CustomerNaoEncontradoError, UserNaoEncontradoError)):
        return HTTPException(status_code=404, detail=str(erro))

    if isinstance(erro, ValorTicketInvalidoError):
        return HTTPException(status_code=400, detail=str(erro))

    return HTTPException(status_code=400, detail=str(erro))


app.include_router(auth_router)
app.include_router(chatwoot_router)
app.include_router(
    customers_router,
    dependencies=[Depends(obter_usuario_autenticado)],
)
app.include_router(
    tickets_router,
    dependencies=[Depends(obter_usuario_autenticado)],
)
