from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from Tickets.models import Ticket, TicketMessage


class TicketRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar(
        self,
        *,
        customer_id: UUID,
        title: str,
        description: str | None = None,
        assigned_user_id: UUID | None = None,
        status: str = "open",
        priority: str = "medium",
        source: str = "platform",
        category: str = "outros",
        intent: str | None = None,
        classification_confidence: float | None = None,
        classification_reason: str | None = None,
        requires_human: bool = False,
        ai_summary: str | None = None,
    ) -> Ticket:
        ticket = Ticket(
            customer_id=customer_id,
            assigned_user_id=assigned_user_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            source=source,
            category=category,
            intent=intent,
            classification_confidence=classification_confidence,
            classification_reason=classification_reason,
            requires_human=requires_human,
            ai_summary=ai_summary,
        )
        self.session.add(ticket)
        self.session.flush()
        self.session.refresh(ticket)
        return ticket

    def obter_por_id(self, ticket_id: UUID, *, carregar_mensagens: bool = False) -> Ticket | None:
        statement = select(Ticket).where(Ticket.id == ticket_id)

        if carregar_mensagens:
            statement = statement.options(selectinload(Ticket.messages))

        return self.session.execute(statement).scalar_one_or_none()

    def listar(
        self,
        *,
        status: str | None = None,
        assigned_user_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Ticket]:
        statement = select(Ticket)

        if status:
            statement = statement.where(Ticket.status == status)

        if assigned_user_id:
            statement = statement.where(Ticket.assigned_user_id == assigned_user_id)

        statement = statement.order_by(
            Ticket.last_message_at.desc().nullslast(),
            Ticket.created_at.desc(),
        ).limit(limit).offset(offset)

        return list(self.session.execute(statement).scalars().all())

    def listar_por_status(self, status: str, *, limit: int = 50, offset: int = 0) -> list[Ticket]:
        return self.listar(status=status, limit=limit, offset=offset)

    def listar_por_cliente(self, customer_id: UUID, *, limit: int = 50, offset: int = 0) -> list[Ticket]:
        statement = (
            select(Ticket)
            .where(Ticket.customer_id == customer_id)
            .order_by(Ticket.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.execute(statement).scalars().all())

    def atualizar_status(self, ticket: Ticket, status: str) -> Ticket:
        ticket.status = status
        self.session.flush()
        self.session.refresh(ticket)
        return ticket

    def atribuir_usuario(self, ticket: Ticket, assigned_user_id: UUID | None) -> Ticket:
        ticket.assigned_user_id = assigned_user_id
        self.session.flush()
        self.session.refresh(ticket)
        return ticket


class TicketMessageRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar(
        self,
        *,
        ticket_id: UUID,
        sender_type: str,
        body: str,
        sender_user_id: UUID | None = None,
        sender_customer_id: UUID | None = None,
        metadata: dict | None = None,
        atualizar_ticket: bool = True,
    ) -> TicketMessage:
        message = TicketMessage(
            ticket_id=ticket_id,
            sender_type=sender_type,
            sender_user_id=sender_user_id,
            sender_customer_id=sender_customer_id,
            body=body,
            metadata_=metadata,
        )
        self.session.add(message)
        self.session.flush()
        self.session.refresh(message)

        if atualizar_ticket:
            ticket = self.session.get(Ticket, ticket_id)
            if ticket:
                ticket.last_message_at = message.created_at or datetime.now(timezone.utc)
                self.session.flush()

        return message

    def listar_por_ticket(self, ticket_id: UUID) -> list[TicketMessage]:
        statement = (
            select(TicketMessage)
            .where(TicketMessage.ticket_id == ticket_id)
            .order_by(TicketMessage.created_at.asc())
        )
        return list(self.session.execute(statement).scalars().all())
