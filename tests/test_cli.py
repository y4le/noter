from noter_gpt.cli import search_documents, summarize_document


def test_search_documents(shared_datadir, storage):
    results = search_documents(
        (shared_datadir / "notes" / "countries" / "united_states.txt"), 2, storage
    )
    assert len(results) == 2
    assert [result[0] for result in results] == [
        "countries/canada.txt",
        "countries/japan.txt",
    ]


def test_summarize_document(shared_datadir):
    file_path = shared_datadir / "notes" / "countries" / "united_states.txt"
    with open(file_path, "r", encoding="utf-8") as file:
        source_file_contents = file.read()
    summary = summarize_document(file_path)
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert len(summary) < len(source_file_contents)
