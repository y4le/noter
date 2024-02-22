from noter_gpt.searcher.interface import SearcherInterface
from noter_gpt.searcher.ripgrep_searcher import RipgrepSearcher
from noter_gpt.searcher.native_searcher import NativeSearcher
from noter_gpt.storage import Storage


SEARCHER_PREFERENCE = [RipgrepSearcher, NativeSearcher]


def inject_searcher(storage: Storage = None) -> SearcherInterface:
    for searcher in SEARCHER_PREFERENCE:
        instance = searcher(storage)
        if instance.is_available():
            return instance

    raise AssertionError("No available searchers")
