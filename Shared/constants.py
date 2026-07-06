USER_ROLES = ("admin", "agent", "customer_success")
ASSIGNABLE_TICKET_ROLES = ("agent", "customer_success")

TICKET_STATUSES = ("open", "in_progress", "pending", "resolved", "closed")
DEFAULT_TICKET_STATUS = "open"

TICKET_PRIORITIES = ("low", "medium", "high", "urgent")
DEFAULT_TICKET_PRIORITY = "medium"

TICKET_SOURCES = ("platform", "whatsapp", "email", "api", "manual")
DEFAULT_TICKET_SOURCE = "platform"

TICKET_CATEGORIES = (
    "rastreamento",
    "eventos",
    "checklist",
    "motorista",
    "financeiro",
    "acesso",
    "integracao",
    "bug",
    "duvida_operacional",
    "cancelamento",
    "comercial",
    "suporte",
    "outros",
)
DEFAULT_TICKET_CATEGORY = "outros"

MESSAGE_SENDER_TYPES = ("customer", "user", "ai_agent", "system")
