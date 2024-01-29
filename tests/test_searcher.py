import pytest
from noter_gpt.searcher import NativeSearcher, RipgrepSearcher


@pytest.fixture(params=[NativeSearcher, RipgrepSearcher])
def searcher(request):
    return request.param()


def test_text_search(shared_datadir, searcher):
    root_path = shared_datadir.as_posix()
    results = searcher.text_search("car", root_path)
    assert results == ["notes/car.txt", "notes/google.txt", "notes/plane.txt"]


def test_text_search_smart_case_sensitive(shared_datadir, searcher):
    root_path = shared_datadir.as_posix()
    results = searcher.text_search("Car", root_path)
    assert results == ["notes/car.txt", "notes/google.txt"]


def test_regex_search(shared_datadir, searcher):
    root_path = shared_datadir.as_posix()
    results = searcher.regex_search(r"u...ed", root_path)
    assert results == [
        "notes/canada.txt",
        "notes/cat.txt",
        "notes/facebook.txt",
        "notes/japan.txt",
        "notes/united_states.txt",
        "notes/wiki.txt",
        "notes/youtube.txt",
    ]


def test_regex_search_smart_case_sensitive(shared_datadir, searcher):
    root_path = shared_datadir.as_posix()
    results = searcher.text_search("car", root_path)
    results = searcher.regex_search(r"U...ed", root_path)
    assert results == [
        "notes/canada.txt",
        "notes/cat.txt",
        "notes/facebook.txt",
        "notes/japan.txt",
        "notes/united_states.txt",
        "notes/youtube.txt",
    ]
