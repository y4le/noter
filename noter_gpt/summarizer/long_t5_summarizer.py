from noter_gpt.storage import Storage
from noter_gpt.summarizer.pipeline_summarizer import PipelineSummarizer


class LongT5Summarizer(PipelineSummarizer):
    def __init__(self, storage: Storage = None):
        super().__init__(
            model_name="pszemraj/long-t5-tglobal-base-16384-book-summary",
            storage=storage,
        )
