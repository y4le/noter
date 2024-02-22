from typing import List

import ripgrepy

from noter_gpt.storage import Storage
from noter_gpt.searcher.utils import relativize_paths
from noter_gpt.searcher.interface import SearcherInterface


class RipgrepSearcher(SearcherInterface):
    """Use external ripgrep (rg) command for full text search"""

    def __init__(self, storage: Storage = None):
        self.storage = storage
        if not self.storage:
            self.storage = Storage()

    def text_search(self, text: str) -> List[str]:
        return self._search(text, False)

    def regex_search(self, pattern: str) -> List[str]:
        return self._search(pattern, True)

    def _search(self, pattern: str, is_regex: bool = True) -> List[str]:
        rg = (
            ripgrepy.Ripgrepy(pattern, self.storage.root_path)
            .files_with_matches()
            .smart_case()
        )
        if not is_regex:
            rg = rg.fixed_strings()
        matching_files = rg.run().as_string.split("\n")[:-1]
        return sorted(relativize_paths(matching_files, self.storage.root_path))

    def is_available(self) -> bool:
        try:
            ripgrepy.Ripgrepy("test", ".")
            return True
        except ripgrepy.RipGrepNotFound:
            return False
