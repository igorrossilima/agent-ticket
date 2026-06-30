from typing import Any, Callable

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from Workers.main import executar_fluxo_suporte


FluxoSuporteExecutor = Callable[..., str]

app = FastAPI(
    title="API Agente de Suporte YUV",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    mensagem: str
    top_k: int = Field(default=3, ge=1, le=10)
    provedor_ia: str = "openai"


class ChatResponse(BaseModel):
    resposta: str
    top_k: int
    provedor_ia: str


async def obter_executor_fluxo() -> FluxoSuporteExecutor:
    return executar_fluxo_suporte


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    executor_fluxo: FluxoSuporteExecutor = Depends(obter_executor_fluxo),
) -> ChatResponse:
    mensagem = request.mensagem.strip() if request.mensagem else ""

    if not mensagem:
        raise HTTPException(
            status_code=400,
            detail="A mensagem do usuário não pode ser vazia.",
        )

    provedor_ia = request.provedor_ia.strip() if request.provedor_ia else "openai"
    provedor_ia = provedor_ia or "openai"

    try:
        resposta = executor_fluxo(
            mensagem_usuario=mensagem,
            provedor_ia=provedor_ia,
            top_k=request.top_k,
        )
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar a mensagem.",
        ) from erro

    return ChatResponse(
        resposta=resposta,
        top_k=request.top_k,
        provedor_ia=provedor_ia,
    )
