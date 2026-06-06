from typing import List, Optional

from app.core.config import get_settings
from app.core.logger import configure_logger
from app.core.models import DraftResponse, Evidence
from app.services.feedback_service import FeedbackService


def import_generation_dependencies():
    try:
        from langchain.llms import OpenAI
        return OpenAI
    except ImportError as exc:
        # Fallback dummy LLM for test environments where langchain/OpenAI
        # libraries are not installed. This allows tests that only exercise
        # prompt construction to instantiate `GenerationService`.
        class DummyOpenAI:
            def __init__(self, *args, **kwargs):
                pass

            def __call__(self, prompt):
                return ""

        return DummyOpenAI

logger = configure_logger("INFO")

TASK_PROMPTS = {
    "case_fact_summary": (
        "Produce a concise case fact summary grounded in the retrieved evidence. "
        "Use the exact details from the citations and avoid any unsupported assertions."
    ),
    "notice_summary": (
        "Produce a notice summary suitable for an internal legal memo. "
        "Highlight the notice type, critical dates, parties, and relevant supporting citations."
    ),
    "title_review_summary": (
        "Produce a title review summary that lists title issues, supporting evidence, and observations. "
        "Keep the response anchored to the provided source passages."
    ),
    "document_checklist": (
        "Create a checklist of critical document components and compliance items found in the evidence. "
        "Each item should reference supporting citations."
    ),
}


class GenerationService:
    def __init__(self) -> None:
        self.settings = get_settings()
        OpenAI = import_generation_dependencies()
        self.llm = OpenAI(
            openai_api_key=self.settings.openai_api_key,
            model_name=self.settings.openai_model,
            temperature=0.0,
        )
        self.feedback_service = FeedbackService()

    def generate_draft(
        self,
        document_id,
        evidence: List[Evidence],
        task_type: str = "case_fact_summary",
        additional_instructions: Optional[str] = None,
    ) -> DraftResponse:
        feedback_hints = self.feedback_service.get_feedback_hints(document_id)
        prompt, citation_map = self._build_prompt(
            document_id,
            evidence,
            task_type,
            additional_instructions,
            feedback_hints=feedback_hints,
        )
        logger.info("Generating draft with task_type=%s", task_type)
        completion = self.llm(prompt)
        return DraftResponse(
            document_id=document_id,
            draft_text=completion.strip(),
            evidence=evidence,
            prompt=prompt,
            citation_map=citation_map,
        )

    def _build_prompt(
        self,
        document_id,
        evidence: List[Evidence],
        task_type: str,
        additional_instructions: Optional[str],
        feedback_hints: Optional[list] = None,
    ) -> (str, dict):
        evidence_sections = []
        citation_map = {}
        for index, evidence_item in enumerate(evidence, start=1):
            label = f"[{index}]"
            evidence_sections.append(f"{label} {evidence_item.text.strip()}\nCitation: {evidence_item.citation}")
            citation_map[label] = evidence_item.citation

        task_prompt = TASK_PROMPTS.get(task_type, TASK_PROMPTS["case_fact_summary"])
        if additional_instructions:
            task_prompt += f" Additional instructions: {additional_instructions}"

        if feedback_hints:
            hint_text = "".join([f"- {hint}\n" for hint in feedback_hints])
            task_prompt += f" Use the following operator feedback to refine the structure and tone:\n{hint_text}"

        prompt = (
            f"You are a legal document analysis assistant. Generate a grounded draft for document {document_id}.\n\n"
            "Use only the evidence listed below and cite it in the draft using bracketed references.\n"
            "If information is not in the evidence, say 'Not available in source material.'\n\n"
            "Evidence:\n"
            f"{chr(10).join(evidence_sections)}\n\n"
            "Draft requirements:\n"
            f"{task_prompt}\n\n"
            "Response format:\n"
            "1. Summary\n"
            "2. Evidence citations referenced by bracketed label\n"
            "3. A short conclusion identifying whether more document review is needed.\n"
        )
        return prompt, citation_map
