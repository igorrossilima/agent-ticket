from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Customers.repository import CustomerRepository
from Postgres.config import obter_config_postgres
from Tickets.schemas import (
    TicketAssignmentUpdate,
    TicketClassificationUpdate,
    TicketCreate,
    TicketMessageCreate,
    TicketMessageRead,
    TicketRead,
    TicketStatusUpdate,
)
from Tickets.service import (
    CustomerNaoEncontradoError,
    TicketService,
    UserNaoEncontradoError,
    ValorTicketInvalidoError,
)
from Users.repository import UserRepository


def criar_sessao_teste():
    engine = create_engine(obter_config_postgres().database_url, pool_pre_ping=True)
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection, autoflush=False, autocommit=False, expire_on_commit=False)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


def criar_dados_base(session):
    sufixo = uuid4().hex
    user = UserRepository(session).criar(
        name="Agente Service",
        email=f"service-agent-{sufixo}@example.com",
        password_hash="hash-teste",
    )
    customer = CustomerRepository(session).criar(
        name="Cliente Service",
        email=f"service-customer-{sufixo}@example.com",
    )
    return user, customer


def test_ticket_service_cria_ticket_e_aplica_status_por_mensagem():
    session_generator = criar_sessao_teste()
    session = next(session_generator)

    try:
        user, customer = criar_dados_base(session)
        service = TicketService(session)

        ticket = service.criar_ticket(
            TicketCreate(
                customer_id=customer.id,
                assigned_user_id=user.id,
                title="  Falha no login  ",
                description="  Cliente nao consegue entrar.  ",
                source="api",
            )
        )

        assert ticket.title == "Falha no login"
        assert ticket.description == "Cliente nao consegue entrar."
        assert ticket.status == "open"
        assert ticket.category == "outros"
        assert ticket.requires_human is False

        mensagem_cliente = service.adicionar_mensagem(
            TicketMessageCreate(
                ticket_id=ticket.id,
                sender_type="customer",
                sender_customer_id=customer.id,
                body="  Preciso de ajuda para acessar.  ",
            )
        )

        assert mensagem_cliente.body == "Preciso de ajuda para acessar."
        assert service.obter_ticket(ticket.id).status == "in_progress"

        mensagem_ia = service.adicionar_mensagem(
            TicketMessageCreate(
                ticket_id=ticket.id,
                sender_type="ai_agent",
                body="Tente redefinir sua senha.",
                metadata={"confidence": 0.91, "rag_sources": ["faq-login"]},
            )
        )

        ticket_atualizado = service.obter_ticket(ticket.id)
        ticket_response = TicketRead.model_validate(ticket_atualizado)
        mensagem_response = TicketMessageRead.model_validate(mensagem_ia)

        assert ticket_atualizado.status == "pending"
        assert ticket_atualizado.last_message_at == mensagem_ia.created_at
        assert mensagem_ia.metadata_["confidence"] == 0.91
        assert ticket_response.status == "pending"
        assert mensagem_response.metadata["rag_sources"] == ["faq-login"]
    finally:
        next(session_generator, None)


def test_ticket_service_atualiza_classificacao():
    session_generator = criar_sessao_teste()
    session = next(session_generator)

    try:
        _, customer = criar_dados_base(session)
        service = TicketService(session)
        ticket = service.criar_ticket(
            TicketCreate(
                customer_id=customer.id,
                title="Como vejo eventos?",
            )
        )

        ticket_classificado = service.atualizar_classificacao(
            ticket.id,
            TicketClassificationUpdate(
                category="eventos",
                intent="consultar_eventos",
                classification_confidence=0.87,
                classification_reason="Cliente quer consultar eventos.",
                requires_human=True,
            ),
        )

        assert ticket_classificado.category == "eventos"
        assert ticket_classificado.intent == "consultar_eventos"
        assert ticket_classificado.classification_confidence == 0.87
        assert ticket_classificado.classification_reason == "Cliente quer consultar eventos."
        assert ticket_classificado.requires_human is True
    finally:
        next(session_generator, None)


def test_ticket_service_atualiza_status_e_atribuicao():
    session_generator = criar_sessao_teste()
    session = next(session_generator)

    try:
        user, customer = criar_dados_base(session)
        service = TicketService(session)
        ticket = service.criar_ticket(
            TicketCreate(
                customer_id=customer.id,
                title="Revisar cobranca",
            )
        )

        ticket_atribuido = service.atribuir_usuario(
            ticket.id,
            TicketAssignmentUpdate(assigned_user_id=user.id),
        )
        ticket_fechado = service.atualizar_status(
            ticket.id,
            TicketStatusUpdate(status="closed"),
        )

        assert ticket_atribuido.assigned_user_id == user.id
        assert ticket_fechado.status == "closed"
        assert ticket_fechado.closed_at is not None
    finally:
        next(session_generator, None)


def test_ticket_service_valida_referencias_e_valores():
    session_generator = criar_sessao_teste()
    session = next(session_generator)

    try:
        _, customer = criar_dados_base(session)
        service = TicketService(session)

        with pytest.raises(CustomerNaoEncontradoError):
            service.criar_ticket(
                TicketCreate(
                    customer_id=uuid4(),
                    title="Cliente inexistente",
                )
            )

        with pytest.raises(UserNaoEncontradoError):
            service.criar_ticket(
                TicketCreate(
                    customer_id=customer.id,
                    assigned_user_id=uuid4(),
                    title="Usuario inexistente",
                )
            )

        ticket = service.criar_ticket(
            TicketCreate(
                customer_id=customer.id,
                title="Mensagem invalida",
            )
        )

        with pytest.raises(ValorTicketInvalidoError):
            service.adicionar_mensagem(
                TicketMessageCreate(
                    ticket_id=ticket.id,
                    sender_type="customer",
                    body="Sem customer id.",
                )
            )
    finally:
        next(session_generator, None)
