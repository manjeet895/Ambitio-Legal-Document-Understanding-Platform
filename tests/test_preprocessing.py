from app.services.preprocessing_service import PreprocessingService


def test_extract_metadata_title_and_case_number():
    service = PreprocessingService()
    class DummyDoc:
        text = "NOTICE OF TITLE SEARCH\nCase Number: 2024-TR-0987\nPlaintiff: Horizon Assets Management\nDefendant: Lotus Leasing"
        metadata = type("Meta", (), {"source_filename": "sample.txt", "page_count": 1, "raw_text_length": 0})()

    metadata = service.extract_metadata(DummyDoc())
    assert metadata.title == "NOTICE OF TITLE SEARCH"
    assert metadata.case_number == "2024-TR-0987"
    assert "Horizon Assets Management" in metadata.parties
