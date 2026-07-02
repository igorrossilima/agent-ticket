from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from Postgres.session import obter_sessao_db
from Shared.constants import DEFAULT_TICKET_STATUS, TICKET_STATUSES
from Tickets.schemas import (
    TicketAssignmentUpdate,
    TicketCreate,
    TicketDetailRead,
    TicketMessageCreate,
    TicketMessageCreateRequest,
    TicketMessageRead,
    TicketRead,
    TicketStatusUpdate,
)
from Tickets.service import (
    CustomerNaoEncontradoError,
    TicketNaoEncontradoError,
    TicketService,
    TicketServiceError,
    UserNaoEncontradoError,
    ValorTicketInvalidoError,
)


router = APIRouter(prefix="/tickets", tags=["tickets"])


def obter_ticket_service(
    session: Session = Depends(obter_sessao_db),
) -> TicketService:
    return TicketService(session)


@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def criar_ticket(
    payload: TicketCreate,
    service: TicketService = Depends(obter_ticket_service),
) -> TicketRead:
    try:
        ticket = service.criar_ticket(payload)
        service.session.commit()
        service.session.refresh(ticket)
        return ticket
    except TicketServiceError as erro:
        service.session.rollback()
        raise _converter_erro_servico(erro) from erro


@router.get("", response_model=list[TicketRead])
def listar_tickets(
    status_ticket: str = Query(default=DEFAULT_TICKET_STATUS, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: TicketService = Depends(obter_ticket_service),
) -> list[TicketRead]:
    _validar_status_query(status_ticket)
    return service.listar_por_status(status_ticket, limit=limit, offset=offset)


@router.get("/{ticket_id}", response_model=TicketDetailRead)
def obter_ticket(
    ticket_id: UUID,
    service: TicketService = Depends(obter_ticket_service),
) -> TicketDetailRead:
    try:
        return service.obter_ticket(ticket_id, carregar_mensagens=True)
    except TicketServiceError as erro:
        raise _converter_erro_servico(erro) from erro


@router.patch("/{ticket_id}/status", response_model=TicketRead)
def atualizar_status_ticket(
    ticket_id: UUID,
    payload: TicketStatusUpdate,
    service: TicketService = Depends(obter_ticket_service),
) -> TicketRead:
    try:
        ticket = service.atualizar_status(ticket_id, payload)
        service.session.commit()
        service.session.refresh(ticket)
        return ticket
    except TicketServiceError as erro:
        service.session.rollback()
        raise _converter_erro_servico(erro) from erro


@router.patch("/{ticket_id}/assignment", response_model=TicketRead)
def atribuir_ticket(
    ticket_id: UUID,
    payload: TicketAssignmentUpdate,
    service: TicketService = Depends(obter_ticket_service),
) -> TicketRead:
    try:
        ticket = service.atribuir_usuario(ticket_id, payload)
        service.session.commit()
        service.session.refresh(ticket)
        return ticket
    except TicketServiceError as erro:
        service.session.rollback()
        raise _converter_erro_servico(erro) from erro


@router.post("/{ticket_id}/messages", response_model=TicketMessageRead, status_code=status.HTTP_201_CREATED)
def adicionar_mensagem_ticket(
    ticket_id: UUID,
    payload: TicketMessageCreateRequest,
    service: TicketService = Depends(obter_ticket_service),
) -> TicketMessageRead:
    try:
        message = service.adicionar_mensagem(
            TicketMessageCreate(
                ticket_id=ticket_id,
                sender_type=payload.sender_type,
                sender_user_id=payload.sender_user_id,
                sender_customer_id=payload.sender_customer_id,
                body=payload.body,
                metadata=payload.metadata,
            )
        )
        service.session.commit()
        service.session.refresh(message)
        return message
    except TicketServiceError as erro:
        service.session.rollback()
        raise _converter_erro_servico(erro) from erro


def _validar_status_query(status_ticket: str) -> None:
    if status_ticket not in TICKET_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Status invalido: {status_ticket}.",
        )


def _converter_erro_servico(erro: TicketServiceError) -> HTTPException:
    if isinstance(erro, (TicketNaoEncontradoError, CustomerNaoEncontradoError, UserNaoEncontradoError)):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro))

    if isinstance(erro, ValorTicketInvalidoError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro))

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro))
