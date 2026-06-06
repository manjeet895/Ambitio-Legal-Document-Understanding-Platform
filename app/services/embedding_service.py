import os
from typing import Any, List

from app.core.config import get_settings
from app.core.logger import configure_logger
from app.core.models import DocumentChunk


def import_embedding_dependencies():
    try:
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.vectorstores import Chroma
        return OpenAIEmbeddings, Chroma
    except ImportError:
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import Chroma
            return HuggingFaceEmbeddings, Chroma
        except ImportError:
            try:
                from langchain_classic.embeddings.huggingface import HuggingFaceEmbeddings
                from langchain_classic.vectorstores import Chroma
                return HuggingFaceEmbeddings, Chroma
            except ImportError as exc:
                raise ImportError(
                    "Embedding dependencies are not installed. Install langchain or supporting packages."
                ) from exc

logger = configure_logger("INFO")


class EmbeddingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.persist_directory = self.settings.chroma_persist_dir
        self.embedding_model_name = self.settings.embedding_model
        self.vector_store = None
        self._initialize_vector_store()

    def _initialize_vector_store(self) -> None:
        os.makedirs(self.persist_directory, exist_ok=True)
        embedding_class, Chroma = import_embedding_dependencies()
        embeddings = embedding_class(model_name=self.embedding_model_name)
        try:
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=embeddings,
                collection_name="legal_documents",
            )
            logger.info("Initialized Chroma vector store at %s", self.persist_directory)
        except Exception as error:
            logger.error("Unable to initialize vector store: %s", error)
            raise

    def index_chunks(self, chunks: List[DocumentChunk]) -> None:
        if not self.vector_store:
            self._initialize_vector_store()
        texts = [chunk.text for chunk in chunks]
        metadatas = []
        for chunk in chunks:
            metadata = dict(chunk.metadata)
            metadata["document_id"] = str(chunk.document_id)
            metadata["chunk_id"] = str(chunk.chunk_id)
            metadatas.append(metadata)

        ids = [str(chunk.chunk_id) for chunk in chunks]
        logger.info("Indexing %s document chunks", len(chunks))
        self.vector_store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        self.vector_store.persist()

    def get_vector_store(self) -> Any:
        if not self.vector_store:
            self._initialize_vector_store()
        return self.vector_store
