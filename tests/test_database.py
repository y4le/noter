import os
import pytest
from noter_gpt.database import AnnoyDatabase


@pytest.fixture
def database(storage):
    return AnnoyDatabase(storage=storage)


def test_build_or_update_index(database, storage):
    assert not os.path.exists(storage.built_index_file())
    database.build_or_update_index()
    assert os.path.exists(storage.built_index_file())


def test_find_similar_finds_actually_similar(database, storage):
    database.build_or_update_index()
    cat_file_path = os.path.join(storage.root_path, "countries", "united_states.txt")
    search_results = database.find_similar_to_file(cat_file_path)
    assert search_results[0][0] == "countries/canada.txt"
    assert search_results[1][0] == "countries/japan.txt"


def test_find_similar_respects_n(database, storage):
    database.build_or_update_index()
    search_results = database.find_similar_to_file(
        os.path.join(storage.root_path, "countries", "united_states.txt"), n=1
    )
    assert len(search_results) == 1
