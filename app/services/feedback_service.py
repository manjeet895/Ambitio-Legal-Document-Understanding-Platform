import json
from datetime import datetime
from pathlib import Path
from typing import Dict

from app.core.config import get_settings
from app.core.logger import configure_logger
from app.core.models import FeedbackRequest

logger = configure_logger("INFO")


class FeedbackService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.store_path = Path(self.settings.feedback_store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self.history = self._load_history()

    def _load_history(self) -> Dict[str, dict]:
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as handle:
                    return json.load(handle)
            except json.JSONDecodeError:
                logger.warning("Feedback store is invalid JSON; starting fresh.")
        return {}

    def store_feedback(self, request: FeedbackRequest) -> int:
        logger.info("Storing feedback for document_id=%s", request.document_id)
        key = str(request.document_id)
        entry = {
            "document_id": key,
            "draft_text": request.draft_text,
            "edited_text": request.edited_text,
            "comments": request.comments,
            "saved_at": datetime.utcnow().isoformat(),
            "hint": self._generate_hint(request),
        }
        existing = self.history.get(key, [])
        if not isinstance(existing, list):
            existing = []
        existing.append(entry)
        self.history[key] = existing
        self._persist_history()
        return len(existing)

    def _generate_hint(self, request: FeedbackRequest) -> str:
        original = request.draft_text.strip().splitlines()
        edited = request.edited_text.strip().splitlines()
        hints = []
        for formatted, corrected in zip(original, edited):
            if formatted.strip() != corrected.strip():
                hints.append(f"Prefer text: '{corrected.strip()}' instead of '{formatted.strip()}'.")
        if not hints:
            hints.append("No major draft structure changes detected; preserve grounding citations.")
        return " ".join(hints)

    def _persist_history(self) -> None:
        with open(self.store_path, "w", encoding="utf-8") as handle:
            json.dump(self.history, handle, indent=2)

    def get_feedback_hints(self, document_id) -> list:
        key = str(document_id)
        entries = self.history.get(key, [])
        hints = [entry.get("hint") for entry in entries if entry.get("hint")]
        return hints[-3:]
