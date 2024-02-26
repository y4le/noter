from noter_gpt.storage import Storage

from noter_gpt.summarizer.interface import SummarizerInterface
from noter_gpt.summarizer.bart_summarizer import BartSummarizer
from noter_gpt.summarizer.falconsai_summarizer import FalconsaiSummarizer
from noter_gpt.summarizer.gemma_summarizer import GemmaSummarizer
from noter_gpt.summarizer.openai_summarizer import OpenAISummarizer


def inject_summarizer(
    storage: Storage, use_openai: bool = False, model_name=None
) -> SummarizerInterface:
    if model_name:
        if model_name == "gemma":
            return GemmaSummarizer(storage=storage)
        if model_name == "falconsai":
            return FalconsaiSummarizer(storage=storage)
    if use_openai:
        return OpenAISummarizer(storage=storage)
    return BartSummarizer(storage=storage)
