from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Customers.repository import CustomerRepository
from Postgres.config import obter_config_postgres
from Tickets.repository import TicketMessageRepository, TicketRepository
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


def test_repositories_criam_ticket_com_mensagens():
    session_generator = criar_sessao_teste()
    session = next(session_generator)

    try:
        sufixo = uuid4().hex
        users = UserRepository(session)
        customers = CustomerRepository(session)
        tickets = TicketRepository(session)
        messages = TicketMessageRepository(session)

        user = users.criar(
            name="Agente Teste",
            email=f"agent-{sufixo}@example.com",
            password_hash="hash-teste",
        )
        customer = customers.criar(
            name="Cliente Teste",
            email=f"cliente-{sufixo}@example.com",
            phone="+5511999999999",
        )
        ticket = tickets.criar(
            customer_id=customer.id,
            assigned_user_id=user.id,
            title="Erro ao acessar conta",
            description="Cliente relata falha no login.",
            source="api",
            category="acesso",
            intent="resolver_login",
            classification_confidence=0.82,
            classification_reason="Cliente relata problema de acesso.",
        )

        primeira = messages.criar(
            ticket_id=ticket.id,
            sender_type="customer",
            sender_customer_id=customer.id,
            body="Nao consigo acessar minha conta.",
        )
        segunda = messages.criar(
            ticket_id=ticket.id,
            sender_type="ai_agent",
            body="Tente redefinir sua senha.",
            metadata={"confidence": 0.87, "rag_sources": ["faq-login"]},
        )

        ticket_com_mensagens = tickets.obter_por_id(ticket.id, carregar_mensagens=True)
        mensagens = messages.listar_por_ticket(ticket.id)

        assert ticket_com_mensagens is not None
        assert ticket_com_mensagens.customer_id == customer.id
        assert ticket_com_mensagens.assigned_user_id == user.id
        assert ticket_com_mensagens.status == "open"
        assert ticket_com_mensagens.priority == "medium"
        assert ticket_com_mensagens.category == "acesso"
        assert ticket_com_mensagens.intent == "resolver_login"
        assert ticket_com_mensagens.classification_confidence == 0.82
        assert ticket_com_mensagens.classification_reason == "Cliente relata problema de acesso."
        assert ticket_com_mensagens.requires_human is False
        assert ticket_com_mensagens.last_message_at == segunda.created_at
        assert [mensagem.id for mensagem in mensagens] == [primeira.id, segunda.id]
        assert mensagens[1].metadata_["rag_sources"] == ["faq-login"]
    finally:
        next(session_generator, None)


def test_repositories_buscam_por_email_e_listam_por_status():
    session_generator = criar_sessao_teste()
    session = next(session_generator)

    try:
        sufixo = uuid4().hex
        documento = f"doc-{sufixo[:12]}"
        users = UserRepository(session)
        customers = CustomerRepository(session)
        tickets = TicketRepository(session)

        user = users.criar(
            name="Customer Success",
            email=f"cs-{sufixo}@example.com",
            password_hash="hash-teste",
            role="customer_success",
        )
        customer = customers.criar(
            name="Cliente Status",
            email=f"status-{sufixo}@example.com",
            document=documento,
        )
        ticket = tickets.criar(
            customer_id=customer.id,
            title="Atualizar cadastro",
            assigned_user_id=user.id,
            status="in_progress",
        )

        tickets.atualizar_status(ticket, "pending")
        tickets_por_status = tickets.listar_por_status("pending")

        assert users.obter_por_email(user.email).id == user.id
        assert customers.obter_por_email(customer.email).id == customer.id
        assert customers.obter_por_documento(customer.document).id == customer.id
        assert ticket.id in [item.id for item in tickets_por_status]
    finally:
        next(session_generator, None)
