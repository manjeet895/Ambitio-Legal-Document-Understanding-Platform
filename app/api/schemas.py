from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    document_id: UUID
    filename: str
    extracted_text_snippet: str
    metadata: dict


class DraftRequestSchema(BaseModel):
    document_id: UUID
    task_type: Optional[str] = Field(
        "case_fact_summary",
        description="Type of summary or draft requested; controls prompt shape.",
    )
    prompt_instructions: Optional[str] = Field(
        None,
        description="Optional additional instructions to customize the draft.",
    )
    top_k: Optional[int] = Field(4, description="Number of evidence chunks to retrieve.")


class EvidenceSchema(BaseModel):
    chunk_id: UUID
    document_id: UUID
    text: str
    page_number: Optional[int]
    citation: str
    score: float


class DraftResponseSchema(BaseModel):
    document_id: UUID
    draft_text: str
    evidence: List[EvidenceSchema]
    prompt: str
    citation_map: dict


class FeedbackRequestSchema(BaseModel):
    document_id: UUID
    draft_text: str
    edited_text: str
    comments: Optional[str] = None


class EvaluationResultSchema(BaseModel):
    document_id: UUID
    retrieval_hits: int
    evidence_count: int
    citations_used: int
    feedback_hints_applied: int
    note: Optional[str] = None
