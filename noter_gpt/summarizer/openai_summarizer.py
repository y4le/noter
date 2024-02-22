import os

from openai import OpenAI

from noter_gpt.summarizer.interface import SummarizerInterface
from noter_gpt.storage import Storage
from noter_gpt.summarizer.constants import (
    MAX_SUMMARY_LENGTH_WORDS,
)


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
            f"total length less than {MAX_SUMMARY_LENGTH_WORDS} words."
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
