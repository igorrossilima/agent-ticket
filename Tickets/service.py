from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from Customers.repository import CustomerRepository
from Shared.constants import MESSAGE_SENDER_TYPES, TICKET_PRIORITIES, TICKET_SOURCES, TICKET_STATUSES
from Tickets.models import Ticket, TicketMessage
from Tickets.repository import TicketMessageRepository, TicketRepository
from Tickets.schemas import TicketAssignmentUpdate, TicketCreate, TicketMessageCreate, TicketStatusUpdate
from Users.repository import UserRepository


class TicketServiceError(ValueError):
    pass


class ValorTicketInvalidoError(TicketServiceError):
    pass


class TicketNaoEncontradoError(TicketServiceError):
    pass


class CustomerNaoEncontradoError(TicketServiceError):
    pass


class UserNaoEncontradoError(TicketServiceError):
    pass


class TicketService:
    def __init__(self, session: Session):
        self.session = session
        self.customers = CustomerRepository(session)
        self.users = UserRepository(session)
        self.tickets = TicketRepository(session)
        self.messages = TicketMessageRepository(session)

    def criar_ticket(self, payload: TicketCreate) -> Ticket:
        self._validar_valor_controlado(payload.priority, TICKET_PRIORITIES, "priority")
        self._validar_valor_controlado(payload.source, TICKET_SOURCES, "source")

        if not self.customers.obter_por_id(payload.customer_id):
            raise CustomerNaoEncontradoError("Cliente do ticket nao encontrado.")

        if payload.assigned_user_id and not self.users.obter_por_id(payload.assigned_user_id):
            raise UserNaoEncontradoError("Usuario atribuido ao ticket nao encontrado.")

        return self.tickets.criar(
            customer_id=payload.customer_id,
            assigned_user_id=payload.assigned_user_id,
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            source=payload.source,
            ai_summary=payload.ai_summary,
        )

    def obter_ticket(self, ticket_id: UUID, *, carregar_mensagens: bool = False) -> Ticket:
        ticket = self.tickets.obter_por_id(ticket_id, carregar_mensagens=carregar_mensagens)

        if not ticket:
            raise TicketNaoEncontradoError("Ticket nao encontrado.")

        return ticket

    def listar_por_status(self, status: str, *, limit: int = 50, offset: int = 0) -> list[Ticket]:
        self._validar_valor_controlado(status, TICKET_STATUSES, "status")
        return self.tickets.listar_por_status(status, limit=limit, offset=offset)

    def atualizar_status(self, ticket_id: UUID, payload: TicketStatusUpdate) -> Ticket:
        self._validar_valor_controlado(payload.status, TICKET_STATUSES, "status")
        ticket = self.obter_ticket(ticket_id)

        ticket.status = payload.status
        ticket.closed_at = datetime.now(timezone.utc) if payload.status == "closed" else None
        self.session.flush()
        self.session.refresh(ticket)
        return ticket

    def atribuir_usuario(self, ticket_id: UUID, payload: TicketAssignmentUpdate) -> Ticket:
        ticket = self.obter_ticket(ticket_id)

        if payload.assigned_user_id and not self.users.obter_por_id(payload.assigned_user_id):
            raise UserNaoEncontradoError("Usuario atribuido ao ticket nao encontrado.")

        return self.tickets.atribuir_usuario(ticket, payload.assigned_user_id)

    def adicionar_mensagem(self, payload: TicketMessageCreate) -> TicketMessage:
        self._validar_valor_controlado(payload.sender_type, MESSAGE_SENDER_TYPES, "sender_type")
        ticket = self.obter_ticket(payload.ticket_id)
        self._validar_remetente(payload, ticket)

        message = self.messages.criar(
            ticket_id=payload.ticket_id,
            sender_type=payload.sender_type,
            sender_user_id=payload.sender_user_id,
            sender_customer_id=payload.sender_customer_id,
            body=payload.body,
            metadata=payload.metadata,
        )

        novo_status = self._status_apos_mensagem(payload.sender_type)
        if novo_status:
            ticket.status = novo_status
            ticket.closed_at = None
            self.session.flush()

        return message

    def _validar_remetente(self, payload: TicketMessageCreate, ticket: Ticket) -> None:
        if payload.sender_type == "customer":
            if not payload.sender_customer_id:
                raise ValorTicketInvalidoError("Mensagem de cliente precisa de sender_customer_id.")

            if payload.sender_customer_id != ticket.customer_id:
                raise ValorTicketInvalidoError("Cliente da mensagem nao pertence ao ticket.")

            return

        if payload.sender_type == "user":
            if not payload.sender_user_id:
                raise ValorTicketInvalidoError("Mensagem de usuario precisa de sender_user_id.")

            if not self.users.obter_por_id(payload.sender_user_id):
                raise UserNaoEncontradoError("Usuario remetente nao encontrado.")

            return

        if payload.sender_customer_id and not self.customers.obter_por_id(payload.sender_customer_id):
            raise CustomerNaoEncontradoError("Cliente remetente nao encontrado.")

        if payload.sender_user_id and not self.users.obter_por_id(payload.sender_user_id):
            raise UserNaoEncontradoError("Usuario remetente nao encontrado.")

    @staticmethod
    def _status_apos_mensagem(sender_type: str) -> str | None:
        if sender_type == "customer":
            return "in_progress"

        if sender_type in {"user", "ai_agent"}:
            return "pending"

        return None

    @staticmethod
    def _validar_valor_controlado(value: str, valores_validos: tuple[str, ...], campo: str) -> None:
        if value not in valores_validos:
            raise ValorTicketInvalidoError(f"Valor invalido para {campo}: {value}.")
