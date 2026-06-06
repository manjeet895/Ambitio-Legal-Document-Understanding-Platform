import os
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.api.schemas import (
    DraftRequestSchema,
    DraftResponseSchema,
    EvaluationResultSchema,
    FeedbackRequestSchema,
    UploadResponse,
)
from app.api.dependencies import get_settings
from app.core.config import Settings
from app.services.chunking_service import ChunkingService
from app.services.evaluation_service import EvaluationService
from app.services.feedback_service import FeedbackService
from app.services.generation_service import GenerationService
from app.services.ocr_service import OCRService
from app.services.preprocessing_service import PreprocessingService
from app.services.retrieval_service import RetrievalService
from app.services.embedding_service import EmbeddingService

router = APIRouter()

ocr_service = OCRService()
preprocessing_service = PreprocessingService()
chunking_service = ChunkingService()
embedding_service = EmbeddingService()
retrieval_service = RetrievalService()
# Defer creation of GenerationService to avoid importing heavy/optional
# generation dependencies at module import time (e.g., during tests).
generation_service = None
feedback_service = FeedbackService()
evaluation_service = EvaluationService()


@router.post("/documents/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...), settings: Settings = Depends(get_settings)
) -> Any:
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT uploads are supported.")

    temporary_path = os.path.join("/tmp" if os.name != "nt" else os.getcwd(), file.filename)
    try:
        contents = await file.read()
        with open(temporary_path, "wb") as handle:
            handle.write(contents)

        document = ocr_service.extract_document(file_path=temporary_path, source_filename=file.filename)
        metadata = preprocessing_service.extract_metadata(document)
        chunks = chunking_service.create_chunks(document)
        embedding_service.index_chunks(chunks)

        return UploadResponse(
            document_id=document.metadata.document_id,
            filename=file.filename,
            extracted_text_snippet=document.text[:320].strip().replace("\n", " "),
            metadata=document.metadata.model_dump(),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)


@router.post("/drafts/generate", response_model=DraftResponseSchema)
async def generate_draft(request: DraftRequestSchema) -> Any:
    global generation_service
    if generation_service is None:
        generation_service = GenerationService()
    evidence = retrieval_service.retrieve_evidence(
        request.document_id,
        top_k=request.top_k,
        task_type=request.task_type,
    )
    if not evidence:
        raise HTTPException(status_code=404, detail="No evidence found for the requested document.")

    response = generation_service.generate_draft(
        document_id=request.document_id,
        evidence=evidence,
        task_type=request.task_type,
        additional_instructions=request.prompt_instructions,
    )
    return response


@router.post("/drafts/feedback", response_model=EvaluationResultSchema)
async def submit_feedback(request: FeedbackRequestSchema) -> Any:
    hints_applied = feedback_service.store_feedback(request)
    return EvaluationResultSchema(
        document_id=request.document_id,
        retrieval_hits=0,
        evidence_count=0,
        citations_used=0,
        feedback_hints_applied=hints_applied,
        note="Feedback stored and will shape future draft prompts.",
    )


@router.get("/evaluation/run/{document_id}", response_model=EvaluationResultSchema)
async def run_evaluation(document_id: UUID) -> Any:
    report = evaluation_service.evaluate_document(document_id)
    return report
