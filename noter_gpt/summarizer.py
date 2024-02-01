import os
import hashlib
import json
from abc import ABC, abstractmethod

from openai import OpenAI
from transformers import pipeline

from noter_gpt.storage import Storage

MAX_SUMMARY_LENGTH = 200
MAX_LOCAL_INPUT_CHARS = 4000

CACHE_SIZE = 1000

HUGGINGFACE_SUMMARIZATION_MODELS = [
    "facebook/bart-large-cnn",
    "Falconsai/text_summarization",
]


class SummarizerInterface(ABC):
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
        pass

    @abstractmethod
    def _summarize(self, text: str, context: str = None) -> str:
        pass


class LocalSummarizer(SummarizerInterface):
    def __init__(
        self, storage: Storage = None, model: str = HUGGINGFACE_SUMMARIZATION_MODELS[0]
    ):
        super().__init__(storage=storage)
        self.model = model
        self.summarizer = pipeline("summarization", model=model)

    def _summarize(self, _text: str, _: str = None) -> str:
        # TODO: recursively summarize large files rather than truncating
        text = _text
        if len(text) > MAX_LOCAL_INPUT_CHARS:
            text = text[:MAX_SUMMARY_LENGTH]

        summary = self.summarizer(
            text, max_length=MAX_SUMMARY_LENGTH, min_length=100, do_sample=False
        )
        return summary[0]["summary_text"]

    def _cache_model_key(self) -> str:
        return f"LOCAL_{self.model}"


class OpenAISummarizer(SummarizerInterface):
    def __init__(self, storage: Storage = None, model: str = "gpt-3.5-turbo"):
        super().__init__(storage=storage)
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = model
        self._last_response = None  # debugging

    def _system_prompt(self) -> str:
        return (
            "You are a creative and experienced copywriter. "
            "You only use factual information and try not to add "
            "any new information when summarizing text. "
            "When summarizing text please try your best to keep the "
            f"total length less than {MAX_SUMMARY_LENGTH} words."
        )

    def _summarize_prompt(self, text_to_summarize: str) -> str:
        return (
            "Please write a summary of the "
            "following text using friendly, easy to read language:\n\n"
            '"""'
            f"{text_to_summarize}"
            '"""'
        )

    def _summarize_with_context_prompt(
        self, text_to_summarize: str, context: str
    ) -> str:
        return (
            "Please write a summary of the text marked SUMMARIZE paying particular "
            "attention to what is relevant to the text marked CONTEXT. "
            "Use friendly, easy to read language:\n\n"
            "CONTEXT:"
            '"""'
            f"{context}"
            '"""'
            "\n\n"
            "SUMMARIZE:"
            '"""'
            f"{text_to_summarize}"
            '"""'
        )

    def _summarize(self, text: str, context: str = None) -> str:
        if context:
            prompt_text = self._summarize_with_context_prompt(text, context)
        else:
            prompt_text = self._summarize_prompt(text)

        self._last_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": prompt_text},
            ],
        ).model_dump()

        return self._last_response["choices"][0]["message"]["content"]

    def _cache_model_key(self) -> str:
        return f"OPENAI_{self.model}"


def get_summarizer(storage: Storage, use_openai: bool = False) -> SummarizerInterface:
    if use_openai:
        return OpenAISummarizer(storage=storage)
    return LocalSummarizer(storage=storage)
