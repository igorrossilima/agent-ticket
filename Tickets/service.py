from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from Customers.repository import CustomerRepository
from Shared.constants import (
    ASSIGNABLE_TICKET_ROLES,
    DEFAULT_TICKET_CATEGORY,
    DEFAULT_TICKET_STATUS,
    MESSAGE_SENDER_TYPES,
    TICKET_CATEGORIES,
    TICKET_CHANNELS,
    TICKET_PRIORITIES,
    TICKET_SOURCES,
    TICKET_STATUSES,
)
from Tickets.models import Ticket, TicketMessage
from Tickets.repository import TicketMessageRepository, TicketRepository
from Tickets.schemas import (
    TicketAssignmentUpdate,
    TicketClassificationUpdate,
    TicketCreate,
    TicketMessageCreate,
    TicketStatusUpdate,
)
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
        self._validar_valor_controlado(payload.channel, TICKET_CHANNELS, "channel")
        self._validar_valor_controlado(payload.category, TICKET_CATEGORIES, "category")

        if not self.customers.obter_por_id(payload.customer_id):
            raise CustomerNaoEncontradoError("Cliente do ticket nao encontrado.")

        if payload.assigned_user_id:
            self._obter_usuario_atribuivel(payload.assigned_user_id)

        return self.tickets.criar(
            customer_id=payload.customer_id,
            assigned_user_id=payload.assigned_user_id,
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            source=payload.source,
            channel=payload.channel,
            external_conversation_id=payload.external_conversation_id,
            category=payload.category,
            intent=payload.intent,
            classification_confidence=payload.classification_confidence,
            classification_reason=payload.classification_reason,
            requires_human=payload.requires_human,
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

    def listar_tickets(
        self,
        *,
        status: str | None = DEFAULT_TICKET_STATUS,
        assigned_user_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Ticket]:
        if status:
            self._validar_valor_controlado(status, TICKET_STATUSES, "status")

        return self.tickets.listar(
            status=status,
            assigned_user_id=assigned_user_id,
            limit=limit,
            offset=offset,
        )

    def listar_tickets_ativos_cliente(
        self,
        customer_id: UUID,
        *,
        channel: str | None = None,
        external_conversation_id: str | None = None,
        limit: int = 10,
    ) -> list[Ticket]:
        return self.tickets.listar_ativos_por_cliente(
            customer_id,
            channel=channel,
            external_conversation_id=external_conversation_id,
            limit=limit,
        )

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

        if payload.assigned_user_id:
            self._obter_usuario_atribuivel(payload.assigned_user_id)

        return self.tickets.atribuir_usuario(ticket, payload.assigned_user_id)

    def atualizar_classificacao(
        self,
        ticket_id: UUID,
        payload: TicketClassificationUpdate,
    ) -> Ticket:
        self._validar_valor_controlado(payload.category, TICKET_CATEGORIES, "category")
        ticket = self.obter_ticket(ticket_id)

        ticket.category = payload.category
        ticket.intent = payload.intent
        ticket.classification_confidence = payload.classification_confidence
        ticket.classification_reason = payload.classification_reason
        ticket.requires_human = payload.requires_human
        self.session.flush()
        self.session.refresh(ticket)
        return ticket

    def aplicar_classificacao_agente(
        self,
        ticket_id: UUID,
        classificacao: dict | None,
        *,
        requires_human: bool = False,
    ) -> Ticket:
        payload = self._payload_classificacao_agente(
            classificacao or {},
            requires_human=requires_human,
        )
        return self.atualizar_classificacao(ticket_id, payload)

    def marcar_handoff_humano(self, ticket_id: UUID) -> Ticket:
        ticket = self.obter_ticket(ticket_id)

        ticket.requires_human = True
        ticket.status = "pending"
        ticket.closed_at = None
        self.session.flush()
        self.session.refresh(ticket)
        return ticket

    def listar_mensagens_ticket(self, ticket_id: UUID, *, limit: int | None = None) -> list[TicketMessage]:
        self.obter_ticket(ticket_id)
        mensagens = self.messages.listar_por_ticket(ticket_id)

        if limit is not None and limit > 0:
            return mensagens[-limit:]

        return mensagens

    def adicionar_mensagem(self, payload: TicketMessageCreate) -> TicketMessage:
        self._validar_valor_controlado(payload.sender_type, MESSAGE_SENDER_TYPES, "sender_type")
        ticket = self.obter_ticket(payload.ticket_id)
        self._validar_remetente(payload, ticket)

        message = self.messages.criar(
            ticket_id=payload.ticket_id,
            sender_type=payload.sender_type,
            sender_user_id=payload.sender_user_id,
            sender_customer_id=payload.sender_customer_id,
            external_message_id=payload.external_message_id,
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

    def _obter_usuario_atribuivel(self, user_id: UUID):
        user = self.users.obter_por_id(user_id)

        if not user or not user.is_active:
            raise UserNaoEncontradoError("Usuario atribuido ao ticket nao encontrado.")

        if user.role not in ASSIGNABLE_TICKET_ROLES:
            raise ValorTicketInvalidoError(
                "Ticket so pode ser atribuido a agent ou customer_success."
            )

        return user

    @staticmethod
    def _payload_classificacao_agente(
        classificacao: dict,
        *,
        requires_human: bool = False,
    ) -> TicketClassificationUpdate:
        category = str(classificacao.get("categoria") or DEFAULT_TICKET_CATEGORY).strip()
        if category not in TICKET_CATEGORIES:
            category = DEFAULT_TICKET_CATEGORY

        return TicketClassificationUpdate(
            category=category,
            intent=classificacao.get("intencao"),
            classification_confidence=TicketService._normalizar_confianca(
                classificacao.get("confianca")
            ),
            classification_reason=classificacao.get("justificativa"),
            requires_human=requires_human,
        )

    @staticmethod
    def _normalizar_confianca(value: object) -> float | None:
        if value is None:
            return None

        try:
            confianca = float(value)
        except (TypeError, ValueError):
            return None

        if confianca < 0:
            return 0.0

        if confianca > 1:
            return 1.0

        return confianca
