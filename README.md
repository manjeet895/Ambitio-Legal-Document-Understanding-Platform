# Ambitio AI Intern Assessment

This repository implements a legal document understanding platform for messy legal-style inputs. It ingests scanned or noisy documents, extracts structured content, persists embeddings, retrieves grounded evidence, generates citation-backed drafts, and improves using operator feedback.

## Key Features

- OCR pipeline with `pdfplumber`, `PaddleOCR`, and `pytesseract` fallback
- Structured metadata extraction from noisy legal text
- Chunking pipeline for source-aware vector indexing
- Embeddings stored in ChromaDB with sentence-transformers
- Hybrid retrieval and evidence reranking by document
- Grounded draft generation with OpenAI-compatible LLM prompts
- operator feedback learning loop with prompt adaptation
- REST API with document upload, draft generation, feedback, and evaluation
- Sample documents and unit tests

## Folder Structure

- `app/` - application code
  - `api/` - REST API routes and schemas
  - `services/` - OCR, preprocessing, chunking, embeddings, retrieval, generation, feedback, and evaluation
  - `core/` - configuration, logger, models
- `data/` - sample documents, stored vector database, outputs
- `scripts/` - sample ingestion script
- `tests/` - pytest test suite

## Setup

1. Copy `.env.example` to `.env` and set your OpenAI API key.

```bash
cp .env.example .env
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Initialize the local document index with sample files:

```bash
python scripts/init_index.py
```

4. Start the API:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

- `GET /health`
  - Health check
- `POST /api/documents/upload`
  - Upload a PDF or TXT document for ingestion
- `POST /api/drafts/generate`
  - Generate a grounded draft using retrieved evidence
- `POST /api/drafts/feedback`
  - Submit operator edits to improve future drafts
- `GET /api/evaluation/run/{document_id}`
  - Run evaluation metrics for a document

### Example Draft Request

```json
{
  "document_id": "<document-id>",
  "task_type": "case_fact_summary",
  "prompt_instructions": "Focus on title issues and evidence citations.",
  "top_k": 4
}
```

## Assumptions and Tradeoffs

- The system uses text-based sample inputs and supports OCR for actual PDFs.
- Feedback is implemented as reusable prompt guidance rather than retraining models.
- Grounding is enforced by including retrieved evidence and citation labels in the prompt.
- The repository is designed for a local, production-like proof-of-concept that is modular and extensible.

## Evaluation

Run unit tests with:

```bash
pytest
```

The evaluation framework uses retrieval hit counts, evidence citations, and stored feedback hints to assess performance.
