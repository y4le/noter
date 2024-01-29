import os
import pytest
from noter_gpt.cli import index_documents, search_documents


@pytest.fixture
def index_file(shared_datadir):
    return (shared_datadir / ".noter" / "index.ann").as_posix()


def test_index_documents(shared_datadir, index_file):
    index_documents(shared_datadir.as_posix(), index_file)

    assert os.path.exists(index_file)


def test_search_documents_excludes_self(shared_datadir, index_file):
    test_search_document_path = (shared_datadir / "notes" / "car.txt").as_posix()
    index_documents(shared_datadir.as_posix(), index_file)

    results = search_documents(test_search_document_path, 1, index_file)
    assert len(results) == 1
    assert results[0][0] == test_search_document_path


def test_search_documents(shared_datadir, index_file):
    index_documents(shared_datadir.as_posix(), index_file)

    results = search_documents(
        (shared_datadir / "notes" / "united_states.txt").as_posix(), 2, index_file
    )
    assert len(results) == 2
    assert [result[0] for result in results] == ["notes/canada.txt", "notes/japan.txt"]
