from dataclasses import dataclass
from typing import Callable

from Agents.classifier import Classifier
from Customers.models import Customer
from Customers.repository import CustomerRepository
from Integrations.Chatwoot.schemas import ChatwootMessageRequest
from Tickets.chat_helpers import (
    extrair_classificacao_fluxo,
    extrair_documentos_fluxo,
    extrair_resposta_fluxo,
    formatar_historico_atendimento,
    montar_metadata_mensagem_ia,
    resposta_requer_handoff_humano,
)
from Tickets.models import Ticket
from Tickets.schemas import TicketCreate, TicketMessageCreate
from Tickets.service import TicketService


FluxoSuporteExecutor = Callable[..., object]
STATUS_TICKET_FINALIZADO = {"resolved", "closed"}
HISTORICO_CHAT_LIMITE = 10


@dataclass
class ChatwootProcessResult:
    resposta: str
    ticket: Ticket
    customer: Customer
    created_new_ticket: bool
    requires_human: bool
    classificacao: dict


class ChatwootIntegrationService:
    def __init__(self, session):
        self.session = session
        self.customers = CustomerRepository(session)
        self.tickets = TicketService(session)

    def processar_mensagem(
        self,
        payload: ChatwootMessageRequest,
        *,
        executor_fluxo: FluxoSuporteExecutor,
    ) -> ChatwootProcessResult:
        customer = self._obter_ou_criar_customer(payload)
        classificacao = Classifier(provedor_ia=payload.provedor_ia).executar(payload.message)
        ticket, created_new_ticket = self._obter_ou_criar_ticket(
            payload=payload,
            customer=customer,
            classificacao=classificacao,
        )
        historico_atendimento = formatar_historico_atendimento(
            self.tickets.listar_mensagens_ticket(
                ticket.id,
                limit=HISTORICO_CHAT_LIMITE,
            )
        )

        self.tickets.adicionar_mensagem(
            TicketMessageCreate(
                ticket_id=ticket.id,
                sender_type="customer",
                sender_customer_id=customer.id,
                external_message_id=payload.message_id,
                body=payload.message,
                metadata={
                    "external": self._metadata_externa(payload),
                },
            )
        )

        resultado_fluxo = executor_fluxo(
            mensagem_usuario=payload.message,
            provedor_ia=payload.provedor_ia,
            top_k=payload.top_k,
            historico_atendimento=historico_atendimento,
            classificacao_inicial=classificacao,
        )
        resposta = extrair_resposta_fluxo(resultado_fluxo)
        classificacao_resposta = extrair_classificacao_fluxo(resultado_fluxo) or classificacao
        documentos_rag = extrair_documentos_fluxo(resultado_fluxo)
        requires_human = resposta_requer_handoff_humano(resposta)

        self.tickets.aplicar_classificacao_agente(
            ticket.id,
            classificacao_resposta,
            requires_human=requires_human,
        )
        self.tickets.adicionar_mensagem(
            TicketMessageCreate(
                ticket_id=ticket.id,
                sender_type="ai_agent",
                body=resposta,
                metadata=montar_metadata_mensagem_ia(
                    classificacao=classificacao_resposta,
                    documentos_rag=documentos_rag,
                    top_k=payload.top_k,
                    provedor_ia=payload.provedor_ia,
                    extra={
                        "external": self._metadata_externa(payload),
                    },
                ),
            )
        )

        if requires_human:
            self.tickets.marcar_handoff_humano(ticket.id)

        self.session.flush()
        self.session.refresh(ticket)

        return ChatwootProcessResult(
            resposta=resposta,
            ticket=ticket,
            customer=customer,
            created_new_ticket=created_new_ticket,
            requires_human=requires_human,
            classificacao=classificacao_resposta,
        )

    def _obter_ou_criar_customer(self, payload: ChatwootMessageRequest) -> Customer:
        customer = None

        if payload.contact_id:
            customer = self.customers.obter_por_external_contact_id(
                payload.contact_id,
                external_channel=payload.channel,
            )

        if not customer and payload.contact_phone:
            customer = self.customers.obter_por_phone(payload.contact_phone)

        if not customer and payload.contact_email:
            customer = self.customers.obter_por_email(payload.contact_email)

        if customer:
            return self.customers.atualizar(
                customer,
                name=payload.contact_name or customer.name,
                email=payload.contact_email or customer.email,
                phone=payload.contact_phone or customer.phone,
                document=customer.document,
                external_contact_id=payload.contact_id or customer.external_contact_id,
                external_channel=payload.channel or customer.external_channel,
            )

        return self.customers.criar(
            name=self._nome_customer(payload),
            email=payload.contact_email,
            phone=payload.contact_phone,
            external_contact_id=payload.contact_id,
            external_channel=payload.channel,
        )

    def _obter_ou_criar_ticket(
        self,
        *,
        payload: ChatwootMessageRequest,
        customer: Customer,
        classificacao: dict,
    ) -> tuple[Ticket, bool]:
        if not payload.force_new_ticket:
            ticket = self._buscar_ticket_compativel(payload, customer, classificacao)
            if ticket:
                return ticket, False

        return self._criar_ticket(payload, customer, classificacao), True

    def _buscar_ticket_compativel(
        self,
        payload: ChatwootMessageRequest,
        customer: Customer,
        classificacao: dict,
    ) -> Ticket | None:
        tickets_mesma_conversa = self.tickets.listar_tickets_ativos_cliente(
            customer.id,
            channel=payload.channel,
            external_conversation_id=payload.conversation_id,
            limit=5,
        )

        for ticket in tickets_mesma_conversa:
            if self._ticket_compativel(ticket, classificacao):
                return ticket

        tickets_mesmo_cliente = self.tickets.listar_tickets_ativos_cliente(
            customer.id,
            channel=payload.channel,
            limit=5,
        )

        for ticket in tickets_mesmo_cliente:
            if self._ticket_compativel(ticket, classificacao):
                return ticket

        return None

    @staticmethod
    def _ticket_compativel(ticket: Ticket, classificacao: dict) -> bool:
        if ticket.status in STATUS_TICKET_FINALIZADO:
            return False

        categoria = str(classificacao.get("categoria") or "outros").strip()
        intencao = classificacao.get("intencao")

        if ticket.category == "outros" or categoria == "outros":
            return True

        if ticket.category != categoria:
            return False

        return not ticket.intent or not intencao or ticket.intent == intencao

    def _criar_ticket(
        self,
        payload: ChatwootMessageRequest,
        customer: Customer,
        classificacao: dict,
    ) -> Ticket:
        return self.tickets.criar_ticket(
            TicketCreate(
                customer_id=customer.id,
                title=self._gerar_titulo_ticket(payload.message),
                description=payload.message,
                source="api",
                channel=payload.channel,
                external_conversation_id=payload.conversation_id,
                category=classificacao.get("categoria") or "outros",
                intent=classificacao.get("intencao"),
                classification_confidence=self.tickets._normalizar_confianca(
                    classificacao.get("confianca")
                ),
                classification_reason=classificacao.get("justificativa"),
            )
        )

    @staticmethod
    def _metadata_externa(payload: ChatwootMessageRequest) -> dict:
        return {
            "channel": payload.channel,
            "conversation_id": payload.conversation_id,
            "message_id": payload.message_id,
            "contact_id": payload.contact_id,
        }

    @staticmethod
    def _nome_customer(payload: ChatwootMessageRequest) -> str:
        return (
            payload.contact_name
            or payload.contact_email
            or payload.contact_phone
            or payload.contact_id
            or f"Contato {payload.conversation_id}"
        )

    @staticmethod
    def _gerar_titulo_ticket(mensagem: str) -> str:
        titulo = mensagem.strip().replace("\n", " ")

        if len(titulo) <= 80:
            return titulo

        return f"{titulo[:77].rstrip()}..."
