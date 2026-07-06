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

Se precisar trocar a porta:

```bash
FRONTEND_PORT=5501 python3 frontend/server.py
```

Se a API estiver em outra URL:

```bash
API_BASE_URL=http://localhost:8001 python3 frontend/server.py
```
