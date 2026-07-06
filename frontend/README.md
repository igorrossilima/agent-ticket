# Frontend de teste

Frontend descartavel para testar a API local sem Postman.

## Como rodar

Com a API ja rodando no Docker:

```bash
python3 frontend/server.py
```

Abra no navegador:

```txt
http://localhost:5500
```

O servidor local tambem faz proxy para a API em `http://localhost:8000`, evitando problema de CORS no navegador.

## Como interpretar

- `Criar user` chama `/auth/register` e exige token de admin. Ele cria um operador interno, mas nao faz login automatico.
- `Login` chama `/auth/login`, salva o token e mostra o operador em `Estado do fluxo`.
- `Validar token` chama `/auth/me` e mostra qual operador esta associado ao token atual.
- `Criar customer` cria o cliente final que abre o ticket.
- `Enviar chat` chama `/chat` e depois busca `/tickets/{ticket_id}` para mostrar status, categoria, handoff, classificacao e documentos RAG usados.
- `Buscar historico` atualiza o detalhe do ticket aberto.
- `Fila open`, `Fila pending` e `Minha fila` testam os filtros operacionais de tickets.

Se precisar trocar a porta:

```bash
FRONTEND_PORT=5501 python3 frontend/server.py
```

Se a API estiver em outra URL:

```bash
API_BASE_URL=http://localhost:8001 python3 frontend/server.py
```
