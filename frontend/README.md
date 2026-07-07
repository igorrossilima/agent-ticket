# Frontend React

Aplicacao React/Vite com uma tela inicial de `Visao Geral`.

## Desenvolvimento

```bash
cd frontend
npm install
npm run dev
```

Abra:

```txt
http://localhost:5501
```

O Vite faz proxy de `/api/*` para `http://localhost:8000`.

## Build estatico

```bash
cd frontend
npm run build
python3 server.py
```

O `server.py` serve os arquivos gerados em `frontend/dist` e continua fazendo proxy de `/api/*`.

Para trocar a URL da API:

```bash
API_BASE_URL=http://localhost:8001 npm run dev
```
