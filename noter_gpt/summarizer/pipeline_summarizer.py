import re

from transformers import pipeline

from noter_gpt.storage import Storage
from noter_gpt.summarizer.util import chunk_text
from noter_gpt.summarizer.interface import SummarizerInterface
from noter_gpt.summarizer.constants import (
    MIN_SUMMARY_LENGTH_WORDS,
    MAX_SUMMARY_LENGTH_WORDS,
)


class PipelineSummarizer(SummarizerInterface):
    def __init__(
        self,
        model_name: str,
        min_summary_words: int = MIN_SUMMARY_LENGTH_WORDS,
        max_summary_words: int = MAX_SUMMARY_LENGTH_WORDS,
        storage: Storage = None,
    ):
        super().__init__(storage=storage)
        self.model_name = model_name
        self.min_summary_words = min_summary_words
        self.max_summary_words = max_summary_words
        self.summarizer = pipeline("summarization", model=model_name)

    def _summarize(self, text: str, _: str = None) -> str:
        chunks = chunk_text(text, self.summarizer.tokenizer.model_max_length * 4)
        summaries = []
        for chunk in chunks:
            summary = self._summarize_chunk(chunk)
            summaries.append(summary)
        concatenated_summary = "\n\n".join(summaries)
        if len(re.split(r"\W+", concatenated_summary)) <= self.max_summary_words:
            return concatenated_summary
        return self._summarize(concatenated_summary, _)

    def _summarize_chunk(self, chunk: str) -> str:
        result = self.summarizer(
            chunk,
            min_length=self.min_summary_words,
            max_length=self.max_summary_words,
            do_sample=False,
        )
        return result[0]["summary_text"]

    def _cache_model_key(self) -> str:
        return f"LOCAL_{self.model_name}"
