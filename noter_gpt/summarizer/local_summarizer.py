import re

from transformers import pipeline

from noter_gpt.storage import Storage
from noter_gpt.summarizer.interface import SummarizerInterface
from noter_gpt.summarizer.constants import (
    MIN_SUMMARY_LENGTH_WORDS,
    MAX_SUMMARY_LENGTH_WORDS,
)

MAX_LOCAL_INPUT_CHARS = 4000
HUGGINGFACE_SUMMARIZATION_MODELS = [
    "facebook/bart-large-cnn",
    "Falconsai/text_summarization",
]


class LocalSummarizer(SummarizerInterface):
    def __init__(
        self, storage: Storage = None, model: str = HUGGINGFACE_SUMMARIZATION_MODELS[0]
    ):
        super().__init__(storage=storage)
        self.model = model
        self.summarizer = pipeline("summarization", model=model)

    def _summarize(self, text: str, _: str = None) -> str:
        chunks = chunk_text(text, MAX_LOCAL_INPUT_CHARS)
        summaries = []
        for chunk in chunks:
            summary = self._summarize_chunk(chunk)
            summaries.append(summary)
        concatenated_summary = "\n\n".join(summaries)
        if len(re.split(r"\W+", concatenated_summary)) <= MAX_SUMMARY_LENGTH_WORDS:
            return concatenated_summary
        return self._summarize(concatenated_summary, _)

    def _summarize_chunk(self, chunk: str) -> str:
        result = self.summarizer(
            chunk,
            min_length=MIN_SUMMARY_LENGTH_WORDS,
            max_length=MAX_SUMMARY_LENGTH_WORDS,
            do_sample=False,
        )
        return result[0]["summary_text"]

    def _cache_model_key(self) -> str:
        return f"LOCAL_{self.model}"


def chunk_text(text, chunk_size):
    chunks = []
    while text:
        if len(text) <= chunk_size:
            chunks.append(text)
            break
        else:
            search_start = int(chunk_size * 2 / 3)
            last_paragraph_end = text.rfind("\n\n", search_start, chunk_size)
            if last_paragraph_end != -1:
                # Split at a paragraph boundary if one exists in the final third of the chunk size
                chunks.append(text[:last_paragraph_end])
                text = text[last_paragraph_end + 2 :]  # Skip the paragraph break
            else:
                last_word_break = text.rfind(" ", search_start, chunk_size)
                if last_word_break != -1:
                    # Split at a word break if one exists in the final third of the chunk size
                    chunks.append(text[:last_word_break])
                    text = text[last_word_break + 1 :]  # Skip the space
                else:
                    # Just split at whatever char ends the chunk
                    chunks.append(text[:chunk_size])
                    text = text[chunk_size:]
    return chunks
