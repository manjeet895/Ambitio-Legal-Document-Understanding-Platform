import re
from datetime import datetime
from typing import Dict, List, Optional

from app.core.logger import configure_logger
from app.core.models import Document, DocumentMetadata

logger = configure_logger("INFO")

DATE_PATTERNS = [
    r"\b(\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4})\b",
    r"\b(\w+ \d{1,2}, \d{4})\b",
]

PARTY_PATTERNS = [
    r"(Plaintiff|Defendant|Applicant|Respondent|Claimant)[:\s]+([A-Z][A-Za-z& ,\.]+)",
    r"(Between|Parties)[:\s]+([A-Z].+)"
]

CASE_NUMBER_PATTERN = r"\b(\d{2,4}-[A-Z]{1,5}-\d{3,6}|\d{2,4}[-/]\d{2,6}|[A-Z]{2,5}-\d{3,6})\b"


class PreprocessingService:
    def extract_metadata(self, document: Document) -> DocumentMetadata:
        logger.info("Extracting structured metadata from document")
        raw_text = document.text
        metadata = document.metadata

        metadata.title = self._extract_title(raw_text)
        metadata.case_number = self._find_first_match(raw_text, CASE_NUMBER_PATTERN)
        metadata.parties = self._find_parties(raw_text)
        metadata.date_of_document = self._find_first_match(raw_text, DATE_PATTERNS)
        metadata.extracted_date = datetime.utcnow().isoformat()
        metadata.tags = self._build_tags(raw_text)

        logger.info("Metadata extracted: title=%s case_number=%s", metadata.title, metadata.case_number)
        return metadata

    def _extract_title(self, text: str) -> Optional[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return None
        candidates = [line for line in lines[:6] if len(line) < 120]
        return candidates[0] if candidates else lines[0]

    def _find_first_match(self, text: str, patterns) -> Optional[str]:
        if isinstance(patterns, str):
            patterns = [patterns]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _find_parties(self, text: str) -> List[str]:
        parties = []
        for pattern in PARTY_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                candidate = match.group(2).strip()
                if candidate and candidate not in parties:
                    parties.append(candidate)
        return parties

    def _build_tags(self, text: str) -> List[str]:
        tags = []
        if "notice" in text.lower():
            tags.append("notice")
        if "agreement" in text.lower() or "contract" in text.lower():
            tags.append("agreement")
        if "title" in text.lower() or "property" in text.lower():
            tags.append("title")
        if "plaintiff" in text.lower() or "defendant" in text.lower():
            tags.append("litigation")
        return tags
