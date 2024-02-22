from noter_gpt.storage import Storage

from noter_gpt.summarizer.interface import SummarizerInterface
from noter_gpt.summarizer.local_summarizer import LocalSummarizer
from noter_gpt.summarizer.openai_summarizer import OpenAISummarizer


def inject_summarizer(
    storage: Storage, use_openai: bool = False
) -> SummarizerInterface:
    if use_openai:
        return OpenAISummarizer(storage=storage)
    return LocalSummarizer(storage=storage)
