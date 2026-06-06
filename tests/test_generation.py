from app.services.generation_service import GenerationService
from app.core.models import Evidence


def test_build_prompt_includes_feedback_hints(monkeypatch):
    service = GenerationService()
    service.feedback_service = type(
        "FeedbackStub",
        (),
        {"get_feedback_hints": lambda self, document_id: ["Use a more formal tone."]},
    )()

    evidence = [Evidence(chunk_id="1", document_id="doc1", text="Test evidence text.", page_number=1, citation="sample:1", score=0.1)]
    prompt, citation_map = service._build_prompt(
        document_id="doc1",
        evidence=evidence,
        task_type="case_fact_summary",
        additional_instructions="Focus on key liability points.",
        feedback_hints=["Use a more formal tone."],
    )

    assert "Use a more formal tone." in prompt
    assert "Focus on key liability points." in prompt
    assert citation_map == {"[1]": "sample:1"}
