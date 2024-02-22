from abc import ABC, abstractmethod
from typing import List

from noter_gpt.storage import Storage


class SearcherInterface(ABC):
    """Full text search"""

    @abstractmethod
    def __init__(self, storage: Storage) -> None:
        pass

    @abstractmethod
    def text_search(self, text: str) -> List[str]:
        """Searches for the given text in the documents"""
        pass

    @abstractmethod
    def regex_search(self, pattern: str) -> List[str]:
        """Searches for the given regex pattern in the documents"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the searcher is available for immediate use"""
        pass
