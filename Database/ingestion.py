import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional, Union

from Database.chunkers import BaseChunker, Chunking, RecursiveChunker
from Database.structure import DocumentoRAG


@dataclass
class MarkdownDocument:
    texto: str
    documento_id: str
    metadados: Dict[str, str]


@dataclass
class IngestionResult:
    documento_id: str
    chunk_total: int
    output_path: str


class MarkdownDocumentReader:
    def read(self, caminho_arquivo: str, documento_id: Optional[str] = None) -> MarkdownDocument:
        caminho = self._validar_caminho(caminho_arquivo)
        texto = caminho.read_text(encoding="utf-8")
        documento_id_resolvido = self._resolver_documento_id(caminho, documento_id)

        return MarkdownDocument(
            texto=texto,
            documento_id=documento_id_resolvido,
            metadados={
                "fonte": "markdown",
                "caminho_arquivo": str(caminho.resolve()),
                "nome_arquivo": caminho.name,
            },
        )

    @staticmethod
    def _validar_caminho(caminho_arquivo: str) -> Path:
        if not caminho_arquivo or not caminho_arquivo.strip():
            raise ValueError("O caminho do arquivo markdown nao pode ser vazio.")

        caminho = Path(caminho_arquivo)

        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo markdown nao encontrado: {caminho_arquivo}")

        if not caminho.is_file():
            raise ValueError(f"O caminho informado nao e um arquivo: {caminho_arquivo}")

        if caminho.suffix.lower() != ".md":
            raise ValueError("O arquivo precisa estar no formato .md.")

        return caminho

    @classmethod
    def _resolver_documento_id(cls, caminho: Path, documento_id: Optional[str]) -> str:
        if documento_id is not None:
            documento_id = documento_id.strip()

            if not documento_id:
                raise ValueError("O documento_id nao pode ser vazio.")

            return documento_id

        return cls._slugify(caminho.stem)

    @staticmethod
    def _slugify(valor: str) -> str:
        normalizado = unicodedata.normalize("NFKD", valor)
        ascii_texto = normalizado.encode("ascii", "ignore").decode("ascii")
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_texto.lower()).strip("-")

        if not slug:
            raise ValueError("Nao foi possivel gerar um documento_id a partir do nome do arquivo.")

        return slug


@dataclass
class JsonlChunkWriter:
    output_dir: Union[str, Path] = "outputs/chunks"

    def __post_init__(self):
        if not str(self.output_dir).strip():
            raise ValueError("O diretorio de saida nao pode ser vazio.")

        self.output_dir = Path(self.output_dir)

    def write(self, documentos: Iterable[DocumentoRAG], documento_id: str) -> str:
        documentos = list(documentos)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"{documento_id}.jsonl"

        with output_path.open("w", encoding="utf-8") as file:
            for documento in documentos:
                file.write(
                    json.dumps(
                        documento.model_dump(),
                        ensure_ascii=False,
                    )
                )
                file.write("\n")

        return str(output_path)


@dataclass
class MarkdownIngestionService:
    reader: Optional[MarkdownDocumentReader] = None
    writer: Optional[JsonlChunkWriter] = None
    chunker: Optional[BaseChunker] = None

    def __post_init__(self):
        self.reader = self.reader or MarkdownDocumentReader()
        self.writer = self.writer or JsonlChunkWriter()
        self.chunker = self.chunker or RecursiveChunker(tamanho_chunk=1000, sobreposicao=100)

    def ingestir(self, caminho_arquivo: str, documento_id: Optional[str] = None) -> IngestionResult:
        documento = self.reader.read(caminho_arquivo, documento_id=documento_id)
        documentos_rag = Chunking(self.chunker).gerar_documentos(
            texto=documento.texto,
            documento_id=documento.documento_id,
            metadados=documento.metadados,
        )
        output_path = self.writer.write(documentos_rag, documento.documento_id)

        return IngestionResult(
            documento_id=documento.documento_id,
            chunk_total=len(documentos_rag),
            output_path=output_path,
        )
