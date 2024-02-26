import re

from transformers import AutoTokenizer, AutoModelForCausalLM

from noter_gpt.storage import Storage
from noter_gpt.summarizer.util import chunk_text
from noter_gpt.summarizer.interface import SummarizerInterface
from noter_gpt.summarizer.constants import (
    MAX_SUMMARY_LENGTH_WORDS,
)

MAX_LOCAL_INPUT_CHARS = 4000


class GemmaSummarizer(SummarizerInterface):
    def __init__(self, storage: Storage = None, model_name: str = "google/gemma-2b"):
        super().__init__(storage=storage)
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, device_map="auto"
        )

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
        input_text = f"Summarize the following text:\n\n{chunk}"
        input_ids = self.tokenizer(input_text, return_tensors="pt").to("cuda")

        outputs = self.model.generate(**input_ids)
        return self.tokenizer.decode(outputs[0])

    def _cache_model_key(self) -> str:
        return f"LOCAL_{self.model_name}"
