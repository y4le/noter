import os
import re

from abc import ABC, abstractmethod
from typing import List, Tuple

import ripgrepy

from noter_gpt.storage import Storage


DEFAULT_PATH = "."
ELIGIBLE_EXTENSIONS = [".txt", ".md"]


class SearcherInterface(ABC):
    @abstractmethod
    def __init__(self, storage: Storage) -> None:
        pass

    @abstractmethod
    def text_search(self, text: str) -> List[str]:
        pass

    @abstractmethod
    def regex_search(self, pattern: str) -> List[str]:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass


class NativeSearcher(SearcherInterface):
    def __init__(self, storage: Storage = None):
        self.storage = storage
        if not self.storage:
            self.storage = Storage()

    def text_search(self, text: str) -> List[str]:
        return self._search(text, is_regex=False)

    def regex_search(self, pattern: str) -> List[str]:
        return self._search(pattern, is_regex=True)

    def _search(self, query: str, is_regex: bool = True) -> List[str]:
        matches = []
        for file in self.storage.all_notes():
            if self._search_file(query, file, is_regex):
                matches.append(file)
        return sorted(_relativize_paths(matches, self.storage.root_path))

    def _search_file(self, query: str, file_path: str, is_regex: bool) -> bool:
        is_case_sensitive = self._is_smart_case_sensitive(query)
        with open(file_path, "r") as f:
            for line in f:
                if is_regex:
                    if re.search(
                        query, line, 0 if is_case_sensitive else re.IGNORECASE
                    ):
                        return True
                else:
                    if is_case_sensitive:
                        if query in line:
                            return True
                    else:
                        if query.casefold() in line.casefold():
                            return True

    def _is_smart_case_sensitive(self, text: str) -> bool:
        # return true if any non-lowercase letters are present
        return bool(re.search("[A-Z]", text))

    def is_available(self) -> bool:
        return True


class RipgrepSearcher(SearcherInterface):
    def __init__(self, storage: Storage = None):
        self.storage = storage
        if not self.storage:
            self.storage = Storage()

    def text_search(self, text: str) -> List[str]:
        return self._search(text, False)

    def regex_search(self, pattern: str) -> List[str]:
        return self._search(pattern, True)

    def _search(self, pattern: str, is_regex: bool = True) -> List[str]:
        rg = ripgrepy.Ripgrepy(pattern, self.storage.root_path).files_with_matches().smart_case()
        if not is_regex:
            rg = rg.fixed_strings()
        matching_files = rg.run().as_string.split("\n")[:-1]
        return sorted(_relativize_paths(matching_files, self.storage.root_path))

    def is_available(self) -> bool:
        try:
            ripgrepy.Ripgrepy("test", ".")
            return True
        except ripgrepy.RipGrepNotFound:
            return False


SEARCHER_PREFERENCE = [RipgrepSearcher, NativeSearcher]


def get_searcher(storage: Storage = None) -> SearcherInterface:
    for searcher in SEARCHER_PREFERENCE:
        instance = searcher(storage)
        if instance.is_available():
            return instance

    raise AssertionError("No available searchers")


def _relativize_paths(paths: List[str], root_path: str) -> List[str]:
    return [os.path.relpath(path, root_path) for path in paths]
