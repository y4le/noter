import re
from typing import List

from noter_gpt.storage import Storage
from noter_gpt.searcher.utils import relativize_paths
from noter_gpt.searcher.interface import SearcherInterface


class NativeSearcher(SearcherInterface):
    """Use built in python tools for full text search"""

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
        return sorted(relativize_paths(matches, self.storage.root_path))

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
        # this is the always-available fallback
        return True
