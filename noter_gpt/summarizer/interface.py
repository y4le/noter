import hashlib
import json

from abc import ABC, abstractmethod

from noter_gpt.storage import Storage

CACHE_SIZE = 1000


class SummarizerInterface(ABC):
    """Responsible for handling caching of summary results"""

    def __init__(self, storage: Storage = None):
        self.storage = storage
        if not self.storage:
            self.storage = Storage()

        self.cache = self._load_cache()

    def _load_cache(self) -> None:
        try:
            with open(self.storage.summary_cache_file(), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_cache(self) -> None:
        with open(self.storage.summary_cache_file(), "w+") as f:
            json.dump(self.cache, f)

    def _get_key(self, text: str, context: str = None) -> str:
        total_text = text + context if context else text
        hash = hashlib.md5(total_text.encode("utf-8")).hexdigest()
        return f"{self._cache_model_key()}__{hash}"

    def _get_from_cache(self, key: str) -> str:
        return self.cache.get(key)

    def _add_to_cache(self, key: str, value: str) -> None:
        if len(self.cache) >= CACHE_SIZE:
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value
        self._save_cache()

    def summarize_text(self, text: str, context: str = None) -> str:
        text_hash = self._get_key(text, context)
        cached_summary = self._get_from_cache(text_hash)
        if cached_summary:
            return cached_summary
        else:
            summary = self._summarize(text, context)
            self._add_to_cache(text_hash, summary)
            return summary

    def summarize_file(self, filepath: str, context: str = None) -> str:
        with open(filepath, "r", encoding="utf-8") as file:
            text = file.read()
        return self.summarize_text(text, context)

    @abstractmethod
    def _cache_model_key(self) -> str:
        """Should return a unique string that identifies the model"""
        pass

    @abstractmethod
    def _summarize(self, text: str, context: str = None) -> str:
        """Should return a summary of the text, optionally taking into account the given context"""
        pass
