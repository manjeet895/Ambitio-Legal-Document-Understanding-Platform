import math
from typing import List, Optional

from app.core.logger import configure_logger
from app.core.models import Document, DocumentChunk

logger = configure_logger("INFO")

CHUNK_WORD_LIMIT = 160


class ChunkingService:
    def create_chunks(self, document: Document) -> List[DocumentChunk]:
        logger.info("Creating document chunks for document %s", document.metadata.document_id)
        paragraphs = [p.strip() for p in document.text.split("\n\n") if p.strip()]
        chunks = []
        for page_number, page_text in enumerate(document.pages, start=1):
            page_chunks = self._chunk_text(page_text)
            for index, chunk_text in enumerate(page_chunks, start=1):
                citation = f"{document.metadata.source_filename or 'document'}:page:{page_number}:chunk:{index}"
                chunks.append(
                    DocumentChunk(
                        document_id=document.metadata.document_id,
                        page_number=page_number,
                        text=chunk_text,
                        metadata={
                            "page_number": page_number,
                            "chunk_index": index,
                            "source": document.metadata.source_filename,
                            "citation": citation,
                        },
                        citation=citation,
                    )
                )
        if not chunks and document.text:
            chunks.append(
                DocumentChunk(
                    document_id=document.metadata.document_id,
                    page_number=None,
                    text=document.text,
                    metadata={"source": document.metadata.source_filename, "citation": "full-document"},
                    citation="full-document",
                )
            )
        logger.info("Created %s chunks", len(chunks))
        return chunks

    def _chunk_text(self, text: str) -> List[str]:
        words = text.split()
        if len(words) <= CHUNK_WORD_LIMIT:
            return [text]

        chunks = []
        chunk_count = math.ceil(len(words) / CHUNK_WORD_LIMIT)
        for index in range(chunk_count):
            start = index * CHUNK_WORD_LIMIT
            end = min(len(words), start + CHUNK_WORD_LIMIT)
            chunks.append(" ".join(words[start:end]))
        return chunks
