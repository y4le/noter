import os
import re

from abc import ABC, abstractmethod
from typing import List, Tuple

import ripgrepy


DEFAULT_PATH = '.'
ELIGIBLE_EXTENSIONS = ['.txt', '.md']


class SearcherInterface(ABC):
    @abstractmethod
    def text_search(self, text: str, root_path: str = DEFAULT_PATH) -> List[str]:
        pass

    @abstractmethod
    def regex_search(self, pattern: str, root_path: str = DEFAULT_PATH) -> List[str]:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass


class NativeSearcher(SearcherInterface):
    def text_search(self, text: str, root_path: str = DEFAULT_PATH) -> List[str]:
        return self._search(text, root_path, is_regex=False)

    def regex_search(self, pattern: str, root_path: str = DEFAULT_PATH) -> List[str]:
        return self._search(pattern, root_path, is_regex=True)

    def _search(self, query: str, root_path: str = DEFAULT_PATH, is_regex: bool = True) -> List[str]:
        matches = []
        for root, dirs, files in os.walk(root_path):
            for file in files:
                if os.path.splitext(file)[-1] not in ELIGIBLE_EXTENSIONS:
                    continue
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    for line in f:
                        if (is_regex and re.search(query, line)) or (not is_regex and query in line):
                            matches.append(file_path)
                            break
        return _relativize_paths(matches, root_path)

    def is_available(self) -> bool:
        return True


class RipgrepSearcher(SearcherInterface):
    def text_search(self, text: str, root_path: str = DEFAULT_PATH) -> List[str]:
      return self._search(text, root_path, False)

    def regex_search(self, pattern: str, root_path: str = DEFAULT_PATH) -> List[str]:
      return self._search(pattern, root_path, True)

    def _search(self, pattern: str, root_path: str = DEFAULT_PATH, is_regex: bool = True) -> List[str]:
        rg = ripgrepy.Ripgrepy(pattern, root_path).files_with_matches()
        if not is_regex:
          rg = rg.ignore_case().files_with_matches().fixed_strings()
        matching_files = rg.run().as_string.split('\n')[:-1]
        return _relativize_paths(matching_files, root_path)

    def is_available(self) -> bool:
        try:
            ripgrepy.Ripgrepy('test', '.')
            return True
        except ripgrepy.RipGrepNotFound:
            return False


SEARCHER_PREFERENCE = [
    RipgrepSearcher,
    NativeSearcher
]

def get_searcher() -> SearcherInterface:
    for searcher in SEARCHER_PREFERENCE:
        instance = searcher()
        if instance.is_available():
            return instance
    
    raise AssertionError('No available searchers')

def _relativize_paths(paths: List[str], root_path: str) -> List[str]:
    return [os.path.relpath(path, root_path) for path in paths]