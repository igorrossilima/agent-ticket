# Integracao Chatwoot/AkrozXP

Endpoint normalizado para receber mensagem do canal externo:

```txt
POST /integrations/chatwoot/messages
```

Payload minimo:

```json
{
  "message": "Como vejo eventos de velocidade?",
  "conversation_id": "123",
  "contact_id": "456",
  "contact_name": "Cliente Exemplo",
  "contact_email": "cliente@example.com",
  "contact_phone": "+5511999999999",
  "channel": "chatwoot"
}
```

Regras principais:

- `contact_id`, telefone ou email identificam/criam o `customer`.
- `conversation_id` identifica a conversa externa, mas nao e unico por ticket.
- Um mesmo customer/conversa pode gerar varios tickets quando o assunto muda.
- Ticket ativo compativel por categoria/intencao e reutilizado.
- Ticket `resolved` ou `closed` nao e reutilizado.
- A resposta retorna `ticket_id`, `customer_id`, categoria, status e se criou ticket novo.

Seguranca opcional:

```env
CHATWOOT_WEBHOOK_TOKEN=token-compartilhado
```

Quando essa variavel existe, a chamada precisa enviar:

```txt
X-Chatwoot-Token: token-compartilhado
```
