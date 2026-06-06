import os
import tempfile

from app.services.feedback_service import FeedbackService
from app.core.models import FeedbackRequest


def test_feedback_store_and_hint_generation(tmp_path):
    feedback_file = tmp_path / "feedback_history.json"
    os.environ["FEEDBACK_STORE_PATH"] = str(feedback_file)
    service = FeedbackService()

    request = FeedbackRequest(
        document_id="12345",
        draft_text="Initial summary line.\nAnother sentence.",
        edited_text="Revised summary line.\nAnother sentence.",
        comments="Correction applied",
    )

    count = service.store_feedback(request)
    assert count == 1
    hints = service.get_feedback_hints(request.document_id)
    assert len(hints) == 1
    assert "Revised summary line." in hints[0]
