from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.core.logger import configure_logger

settings = get_settings()
logger = configure_logger(settings.log_level)

app = FastAPI(
    title="Ambitio Legal Document Understanding Platform",
    description="A grounded document ingestion, retrieval, and draft generation API for legal-style workflows.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting Ambitio AI platform")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "ambitio_ai_platform"}
