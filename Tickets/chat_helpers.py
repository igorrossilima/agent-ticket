import unicodedata

from fastapi.encoders import jsonable_encoder


def extrair_resposta_fluxo(resultado_fluxo) -> str:
    if isinstance(resultado_fluxo, str):
        return resultado_fluxo

    return resultado_fluxo.resposta


def extrair_classificacao_fluxo(resultado_fluxo) -> dict | None:
    if isinstance(resultado_fluxo, str):
        return None

    return getattr(resultado_fluxo, "classificacao", None)


def extrair_documentos_fluxo(resultado_fluxo) -> list:
    if isinstance(resultado_fluxo, str):
        return []

    return getattr(resultado_fluxo, "documentos", None) or []


def montar_metadata_mensagem_ia(
    *,
    classificacao: dict | None,
    documentos_rag: list,
    top_k: int,
    provedor_ia: str,
    extra: dict | None = None,
) -> dict:
    metadata = {
        "classification": jsonable_encoder(classificacao or {}),
        "rag_docs": serializar_documentos_rag(documentos_rag),
        "top_k": top_k,
        "provedor_ia": provedor_ia,
    }

    if extra:
        metadata.update(jsonable_encoder(extra))

    return metadata


def serializar_documentos_rag(documentos_rag: list) -> list[dict]:
    documentos = []

    for documento in documentos_rag:
        documentos.append(
            jsonable_encoder(
                {
                    "id": getattr(documento, "id", None),
                    "score": getattr(documento, "score", None),
                    "metadata": getattr(documento, "metadados", {}) or {},
                    "text": getattr(documento, "text", ""),
                }
            )
        )

    return documentos


def formatar_historico_atendimento(mensagens: list) -> str:
    if not mensagens:
        return ""

    rotulos = {
        "customer": "Cliente",
        "user": "Atendente",
        "ai_agent": "Agente IA",
        "system": "Sistema",
    }
    linhas = []

    for mensagem in mensagens:
        rotulo = rotulos.get(mensagem.sender_type, mensagem.sender_type)
        linhas.append(f"{rotulo}: {mensagem.body}")

    return "\n".join(linhas)


def resposta_requer_handoff_humano(resposta: str) -> bool:
    texto = normalizar_texto_busca(resposta)
    frases_handoff = (
        "nao encontrei informacao suficiente",
        "nao encontrou informacao suficiente",
        "nao ha informacao suficiente",
        "nao existe informacao suficiente",
        "sem informacao suficiente",
    )
    return any(frase in texto for frase in frases_handoff)


def normalizar_texto_busca(texto: str) -> str:
    texto_normalizado = unicodedata.normalize("NFKD", texto or "")
    texto_sem_acentos = "".join(
        char for char in texto_normalizado if not unicodedata.combining(char)
    )
    return texto_sem_acentos.lower()
