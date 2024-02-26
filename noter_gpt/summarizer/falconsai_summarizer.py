from noter_gpt.storage import Storage
from noter_gpt.summarizer.pipeline_summarizer import PipelineSummarizer


class FalconsaiSummarizer(PipelineSummarizer):
    def __init__(self, storage: Storage = None):
        super().__init__(
            model_name="Falconsai/text_summarization",
            storage=storage,
        )
