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

## Quando a tela nao atualiza

Problema ja observado: um processo antigo do Vite pode continuar segurando a porta `5501`, ou o cache em `frontend/node_modules/.vite` pode manter modulos antigos. O sintoma e uma tela atualizar parcialmente, enquanto outra pagina continua com layout antigo.

Checklist antes de validar mudancas visuais:

```bash
ps -ef | rg 'vite|npm run dev'
ss -ltnp | rg ':5501'
```

Se houver mais de um processo Vite, pare os antigos e limpe o cache:

```bash
pkill -f 'vite --host'
rm -rf frontend/node_modules/.vite
cd frontend
npm run dev
```

No navegador, usar hard refresh:

```txt
Ctrl + Shift + R
```
