import os
from pathlib import Path
from typing import List, Optional

from app.core.logger import configure_logger
from app.core.models import DocumentChunk, DocumentMetadata


def import_ocr_dependencies():
    try:
        import pdfplumber
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise ImportError(
            "OCR dependencies are not installed. Install pdfplumber, pytesseract, and Pillow."
        ) from exc

    try:
        from paddleocr import PaddleOCR
    except ImportError:
        PaddleOCR = None

    return pdfplumber, pytesseract, PaddleOCR, Image

logger = configure_logger("INFO")


def safe_read_pdf(file_path: str) -> List[str]:
    pdfplumber, _, _, _ = import_ocr_dependencies()
    pages: List[str] = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages.append(text)
    except Exception as error:
        logger.warning("PDF parsing failed: %s", error)
    return pages


def paddle_ocr_pdf(file_path: str) -> List[str]:
    pdfplumber, _, PaddleOCR, _ = import_ocr_dependencies()
    if PaddleOCR is None:
        logger.warning("PaddleOCR is not installed; skipping PaddleOCR stage.")
        return []

    ocr = PaddleOCR(use_angle_cls=True, lang="en", use_gpu=False)
    pages: List[str] = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                image = page.to_image(resolution=300).original
                raw = ocr.ocr(image, cls=True)
                page_text = "\n".join(
                    [line[1][0] for result in raw for line in result]
                )
                pages.append(page_text)
    except Exception as error:
        logger.warning("PaddleOCR failed: %s", error)
    return pages


def tesseract_fallback(file_path: str) -> List[str]:
    pdfplumber, pytesseract, _, _ = import_ocr_dependencies()
    pages: List[str] = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                image = page.to_image(resolution=300).original
                text = pytesseract.image_to_string(image)
                pages.append(text)
    except Exception as error:
        logger.error("Tesseract fallback failed: %s", error)
    return pages


class OCRService:
    def extract_document(self, file_path: str, source_filename: Optional[str] = None) -> "Document":
        logger.info("Extracting document from %s", file_path)
        suffix = Path(file_path).suffix.lower()
        if suffix == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
                content = handle.read()
            text_pages = [content]
        else:
            text_pages = safe_read_pdf(file_path)
            if not any(text_pages):
                logger.info("No native text recovered; falling back to OCR.")
                text_pages = paddle_ocr_pdf(file_path)

            if not any(text_pages):
                logger.info("PaddleOCR failed; using Tesseract fallback.")
                text_pages = tesseract_fallback(file_path)

        full_text = "\n\n".join(page for page in text_pages if page)
        metadata = DocumentMetadata(
            source_filename=source_filename,
            page_count=len(text_pages),
            raw_text_length=len(full_text),
        )
        return Document(text=full_text, pages=text_pages, metadata=metadata)


class Document:
    def __init__(self, text: str, pages: List[str], metadata: DocumentMetadata) -> None:
        self.text = text
        self.pages = pages
        self.metadata = metadata
