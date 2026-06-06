from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_id: str = Field(default_factory=lambda: str(uuid4()))
    title: Optional[str] = None
    source_filename: Optional[str] = None
    extracted_date: Optional[str] = None
    parties: Optional[List[str]] = None
    case_number: Optional[str] = None
    date_of_document: Optional[str] = None
    raw_text_length: int = 0
    page_count: int = 0
    tags: List[str] = []


class Document:
    def __init__(self, text: str, pages: List[str], metadata: DocumentMetadata) -> None:
        self.text = text
        self.pages = pages
        self.metadata = metadata


class DocumentChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    page_number: Optional[int]
    text: str
    metadata: Dict[str, Any] = {}
    citation: str = ""


class Evidence(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    page_number: Optional[int]
    citation: str
    score: float


class DraftRequest(BaseModel):
    document_id: str
    task_type: str = "case_fact_summary"
    prompt_instructions: Optional[str] = None
    top_k: int = 4


class DraftResponse(BaseModel):
    document_id: str
    draft_text: str
    evidence: List[Evidence]
    prompt: str
    citation_map: Dict[str, str]


class FeedbackRequest(BaseModel):
    document_id: str
    draft_text: str
    edited_text: str
    comments: Optional[str] = None


class EvaluationReport(BaseModel):
    document_id: str
    retrieval_hits: int
    evidence_count: int
    citations_used: int
    feedback_hints_applied: int
    note: Optional[str] = None
