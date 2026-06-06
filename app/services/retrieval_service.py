import os
from typing import List

from app.core.config import get_settings
from app.core.logger import configure_logger
from app.core.models import Evidence
from app.services.embedding_service import EmbeddingService

logger = configure_logger("INFO")


class RetrievalService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.embedding_service = EmbeddingService()
        self._load_document_index()

    def _load_document_index(self) -> None:
        index_path = os.path.join(self.settings.chroma_persist_dir, "document_index.json")
        logger.debug("Document index path %s", index_path)

    def retrieve_evidence(self, document_id, top_k: int = 4, task_type: str = "case_fact_summary") -> List[Evidence]:
        vector_store = self.embedding_service.get_vector_store()
        query = self._query_for_task(document_id, task_type)
        logger.info("Retrieving evidence for document_id=%s task_type=%s top_k=%s", document_id, task_type, top_k)
        results = vector_store.similarity_search_with_score(
            query,
            k=top_k,
            filter={"document_id": str(document_id)},
        )
        evidence = []
        for doc, score in results:
            metadata = getattr(doc, "metadata", {}) or {}
            page_number = metadata.get("page_number")
            citation = metadata.get("citation", "unknown")
            evidence.append(
                Evidence(
                    chunk_id=metadata.get("chunk_id"),
                    document_id=document_id,
                    text=getattr(doc, "page_content", str(doc)),
                    page_number=page_number,
                    citation=citation,
                    score=float(score),
                )
            )
        return evidence

    def _query_for_task(self, document_id: str, task_type: str) -> str:
        if task_type == "notice_summary":
            return f"Notice summary evidence for document {document_id}"
        if task_type == "title_review_summary":
            return f"Title review evidence for document {document_id}"
        if task_type == "document_checklist":
            return f"Checklist items for document {document_id}"
        return f"Case facts and title evidence for document {document_id}"
