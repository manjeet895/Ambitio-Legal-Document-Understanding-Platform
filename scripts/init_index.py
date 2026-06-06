import os
from pathlib import Path

from app.services.ocr_service import OCRService
from app.services.preprocessing_service import PreprocessingService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService


def ingest_sample_documents(samples_dir: str) -> None:
    ocr_service = OCRService()
    preprocessing_service = PreprocessingService()
    chunking_service = ChunkingService()
    embedding_service = EmbeddingService()

    sample_path = Path(samples_dir)
    for sample_file in sample_path.glob("*.txt"):
        document = ocr_service.extract_document(str(sample_file), source_filename=sample_file.name)
        preprocessing_service.extract_metadata(document)
        chunks = chunking_service.create_chunks(document)
        embedding_service.index_chunks(chunks)
        print(f"Indexed {len(chunks)} chunks for {sample_file.name}")


if __name__ == "__main__":
    ingest_sample_documents("./data/samples")
