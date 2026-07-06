from functools import lru_cache
from typing import Callable

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from Integrations.Chatwoot.schemas import ChatwootMessageRequest, ChatwootMessageResponse
from Integrations.Chatwoot.service import ChatwootIntegrationService
from Postgres.session import obter_sessao_db
from Workers.main import executar_fluxo_suporte_detalhado


FluxoSuporteExecutor = Callable[..., object]
router = APIRouter(prefix="/integrations/chatwoot", tags=["integrations"])


class ChatwootSettings(BaseSettings):
    chatwoot_webhook_token: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def obter_chatwoot_settings() -> ChatwootSettings:
    return ChatwootSettings()


def obter_chatwoot_service(
    session: Session = Depends(obter_sessao_db),
) -> ChatwootIntegrationService:
    return ChatwootIntegrationService(session)


async def obter_executor_fluxo() -> FluxoSuporteExecutor:
    return executar_fluxo_suporte_detalhado


def validar_webhook_token(
    x_chatwoot_token: str | None = Header(default=None),
    settings: ChatwootSettings = Depends(obter_chatwoot_settings),
) -> None:
    if not settings.chatwoot_webhook_token:
        return

    if x_chatwoot_token != settings.chatwoot_webhook_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token do webhook invalido.",
        )


@router.post(
    "/messages",
    response_model=ChatwootMessageResponse,
    dependencies=[Depends(validar_webhook_token)],
)
async def receber_mensagem_chatwoot(
    payload: ChatwootMessageRequest,
    service: ChatwootIntegrationService = Depends(obter_chatwoot_service),
    executor_fluxo: FluxoSuporteExecutor = Depends(obter_executor_fluxo),
) -> ChatwootMessageResponse:
    try:
        resultado = await run_in_threadpool(
            service.processar_mensagem,
            payload,
            executor_fluxo=executor_fluxo,
        )
        service.session.commit()
        service.session.refresh(resultado.ticket)
        return ChatwootMessageResponse(
            resposta=resultado.resposta,
            ticket_id=resultado.ticket.id,
            customer_id=resultado.customer.id,
            created_new_ticket=resultado.created_new_ticket,
            status=resultado.ticket.status,
            category=resultado.ticket.category,
            intent=resultado.ticket.intent,
            requires_human=resultado.ticket.requires_human,
            should_reply=True,
        )
    except ValueError as erro:
        service.session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro)) from erro
    except Exception as erro:
        service.session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar webhook do Chatwoot.",
        ) from erro
