import pytest
from noter_gpt.searcher.native_searcher import NativeSearcher
from noter_gpt.searcher.ripgrep_searcher import RipgrepSearcher


@pytest.fixture(params=[NativeSearcher, RipgrepSearcher])
def searcher(request, storage):
    return request.param(storage=storage)


def test_text_search(searcher):
    results = searcher.text_search("car")
    assert results == [
        "car.txt",
        "people/elon.txt",
        "plane.txt",
        "websites/google.txt",
    ]


def test_text_search_smart_case_sensitive(searcher):
    results = searcher.text_search("Car")
    assert results == ["car.txt", "people/elon.txt", "websites/google.txt"]


def test_regex_search(searcher):
    results = searcher.regex_search(r"u...ed")
    assert results == [
        "animals/cat.txt",
        "countries/canada.txt",
        "countries/japan.txt",
        "countries/united_states.txt",
        "people/elon.txt",
        "websites/facebook.txt",
        "websites/wiki.txt",
        "websites/youtube.txt",
    ]


def test_regex_search_smart_case_sensitive(searcher):
    results = searcher.regex_search(r"U...ed")
    assert results == [
        "animals/cat.txt",
        "countries/canada.txt",
        "countries/japan.txt",
        "countries/united_states.txt",
        "people/elon.txt",
        "websites/facebook.txt",
        "websites/youtube.txt",
    ]
