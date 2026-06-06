# Architecture Overview

## System Layers

- `app.main` - FastAPI application entrypoint with health checks and route registration.
- `app.api` - API schemas and route definitions for document ingestion, drafting, feedback, and evaluation.
- `app.services` - Modular service layer implementing OCR, preprocessing, chunking, embedding, retrieval, generation, feedback, and evaluation.
- `app.core` - Configuration, logging, and shared type definitions.
- `data` - Sample documents, generated outputs, persistent Chroma vector store, and feedback history.

## Data Flow

1. Document upload triggers OCR ingestion.
2. OCR service extracts raw text and page metadata from PDF or text input.
3. Preprocessing normalizes text, extracts structured fields, and creates document metadata.
4. Chunking service segments content into manageable chunks with citations and source references.
5. Embedding service transforms chunks into vector embeddings stored in ChromaDB.
6. Retrieval service performs hybrid similarity search and keyword reranking.
7. Generation service assembles evidence-backed prompts and generates a grounded draft with citations.
8. Operator feedback is captured and stored as reusable correction patterns.
9. Future draft generation incorporates feedback hints to improve output.

## Key Design Tradeoffs

- **Simplicity vs. robustness**: The system uses a practical pipeline with OCR fallbacks and metadata extraction heuristics rather than full production OCR tuning.
- **Grounding control**: Prompts explicitly include retrieved evidence and citation references to avoid hallucination.
- **Learning loop**: Feedback is persisted as reusable hints rather than training a model, enabling iterative improvement without complex retraining.
- **Scalability**: The architecture is modular; ChromaDB persists local vectors and can scale to remote vector stores if needed.

## Assumptions

- Input document quality may vary; OCR is best-effort with fallback strategies.
- The system is designed for local evaluation and can be extended to cloud storage and external LLM providers.
- Operator edits are captured as edited sections and reuse patterns in future prompt construction.
