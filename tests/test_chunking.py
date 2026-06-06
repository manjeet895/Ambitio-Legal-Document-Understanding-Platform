from app.services.chunking_service import ChunkingService


def test_chunking_splits_long_text():
    service = ChunkingService()
    text = "".join([f"word{i} " for i in range(350)])
    document = type("Doc", (), {"text": text, "pages": [text], "metadata": type("Meta", (), {"document_id": "1", "source_filename": "sample.txt"})()})

    chunks = service.create_chunks(document)
    assert len(chunks) == 3
    assert all(len(chunk.text.split()) <= 160 for chunk in chunks)


def test_chunking_handles_short_documents():
    service = ChunkingService()
    short_text = "This is a short legal paragraph."
    document = type("Doc", (), {"text": short_text, "pages": [short_text], "metadata": type("Meta", (), {"document_id": "2", "source_filename": "sample.txt"})()})

    chunks = service.create_chunks(document)
    assert len(chunks) == 1
    assert chunks[0].text == short_text
