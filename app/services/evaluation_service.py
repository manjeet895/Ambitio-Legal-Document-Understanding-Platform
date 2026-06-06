import logging
from typing import Optional

from app.core.logger import configure_logger
from app.core.models import EvaluationReport
from app.services.feedback_service import FeedbackService
from app.services.retrieval_service import RetrievalService

logger = configure_logger("INFO")


class EvaluationService:
    def __init__(self) -> None:
        self.retrieval_service = RetrievalService()
        self.feedback_service = FeedbackService()

    def evaluate_document(self, document_id) -> EvaluationReport:
        logger.info("Evaluating document %s", document_id)
        evidence = self.retrieval_service.retrieve_evidence(document_id, top_k=5)
        hints_applied = self._count_feedback_entries(document_id)
        report = EvaluationReport(
            document_id=document_id,
            retrieval_hits=len(evidence),
            evidence_count=len(evidence),
            citations_used=sum(1 for item in evidence if item.citation),
            feedback_hints_applied=hints_applied,
            note="Evaluation uses retrieval evidence count and stored feedback hints.",
        )
        return report

    def _count_feedback_entries(self, document_id) -> int:
        key = str(document_id)
        history = self.feedback_service.history.get(key, [])
        return len(history) if isinstance(history, list) else 0
