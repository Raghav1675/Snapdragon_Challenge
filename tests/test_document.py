from aura.document import chunk_text, normalize_text


def test_text_normalization():
    assert normalize_text("  hello   world \n\n\n test ") == "hello world\n\ntest"


def test_chunking():
    text = " ".join(["word"] * 2500)
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) >= 5
    assert all(c for c in chunks)
