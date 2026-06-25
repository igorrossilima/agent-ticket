import json

import pytest

from Database.chunkers import RecursiveChunker
from Database.ingestion import (
    JsonlChunkWriter,
    MarkdownDocumentReader,
    MarkdownIngestionService,
)


def test_markdown_reader_le_arquivo_valido_com_metadados(tmp_path):
    caminho = tmp_path / "Politica de Reembolso.md"
    caminho.write_text("# Politica\n\nTexto da wiki.", encoding="utf-8")

    documento = MarkdownDocumentReader().read(str(caminho))

    assert documento.texto == "# Politica\n\nTexto da wiki."
    assert documento.documento_id == "politica-de-reembolso"
    assert documento.metadados["fonte"] == "markdown"
    assert documento.metadados["nome_arquivo"] == "Politica de Reembolso.md"
    assert documento.metadados["caminho_arquivo"] == str(caminho.resolve())


def test_markdown_reader_rejeita_caminho_vazio():
    with pytest.raises(ValueError, match="nao pode ser vazio"):
        MarkdownDocumentReader().read("   ")


def test_markdown_reader_rejeita_arquivo_inexistente(tmp_path):
    caminho = tmp_path / "wiki.md"

    with pytest.raises(FileNotFoundError, match="nao encontrado"):
        MarkdownDocumentReader().read(str(caminho))


def test_markdown_reader_rejeita_extensao_diferente_de_md(tmp_path):
    caminho = tmp_path / "wiki.txt"
    caminho.write_text("Texto", encoding="utf-8")

    with pytest.raises(ValueError, match="formato .md"):
        MarkdownDocumentReader().read(str(caminho))


def test_markdown_ingestion_service_gera_jsonl_com_chunks(tmp_path):
    entrada = tmp_path / "Manual Suporte.md"
    entrada.write_text(
        "Primeiro paragrafo com texto.\n\nSegundo paragrafo com outro texto.",
        encoding="utf-8",
    )
    output_dir = tmp_path / "chunks"
    service = MarkdownIngestionService(
        writer=JsonlChunkWriter(output_dir=str(output_dir)),
        chunker=RecursiveChunker(tamanho_chunk=25, sobreposicao=0),
    )

    resultado = service.ingestir(str(entrada))

    assert resultado.documento_id == "manual-suporte"
    assert resultado.chunk_total > 1
    assert resultado.output_path == str(output_dir / "manual-suporte.jsonl")

    linhas = (output_dir / "manual-suporte.jsonl").read_text(encoding="utf-8").splitlines()
    registros = [json.loads(linha) for linha in linhas]

    assert len(registros) == resultado.chunk_total
    assert registros[0]["id"] == "manual-suporte-chunk-1"
    assert registros[0]["text"]
    assert registros[0]["metadados"]["fonte"] == "markdown"
    assert registros[0]["metadados"]["nome_arquivo"] == "Manual Suporte.md"
    assert registros[0]["metadados"]["documento_origem_id"] == "manual-suporte"
    assert registros[0]["metadados"]["chunk_indice"] == 0
    assert registros[0]["metadados"]["chunk_total"] == resultado.chunk_total


def test_markdown_ingestion_service_usa_documento_id_informado(tmp_path):
    entrada = tmp_path / "Nome Qualquer.md"
    entrada.write_text("Conteudo curto.", encoding="utf-8")
    output_dir = tmp_path / "chunks"
    service = MarkdownIngestionService(
        writer=JsonlChunkWriter(output_dir=str(output_dir)),
    )

    resultado = service.ingestir(str(entrada), documento_id="wiki-empresa")

    assert resultado.documento_id == "wiki-empresa"
    assert resultado.output_path == str(output_dir / "wiki-empresa.jsonl")
