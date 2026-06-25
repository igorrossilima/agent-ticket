import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Database.chunkers import Chunking, RecursiveChunker


def main():
    texto = """
    O cliente pode pedir reembolso em ate 7 dias apos a compra.
    Depois desse prazo, o atendimento precisa abrir uma analise manual.

    Para cancelamento, o cliente deve acessar a area de assinaturas.
    Se houver cobranca duplicada, o suporte financeiro deve ser acionado.
    """

    chunker = RecursiveChunker(tamanho_chunk=90, sobreposicao=15)
    chunks = chunker.gerar_chunks(texto)

    print("\n=== Chunks gerados ===\n")
    for indice, chunk in enumerate(chunks, start=1):
        print(f"CHUNK {indice}")
        print(chunk)
        print("-" * 40)

    chunking = Chunking(chunker)
    documentos = chunking.gerar_documentos(
        texto=texto,
        documento_id="manual-suporte",
        metadados={"fonte": "script_manual"},
    )

    print("\n=== DocumentoRAG gerado em memoria ===\n")
    for documento in documentos:
        print(documento.model_dump())
        print("-" * 40)


if __name__ == "__main__":
    main()
