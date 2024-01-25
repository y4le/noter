import os
from abc import ABC, abstractmethod
from openai import OpenAI
from transformers import pipeline

MAX_SUMMARY_LENGTH = 500

HUGGINGFACE_SUMMARIZATION_MODELS = [
    "facebook/bart-large-cnn",
    "Falconsai/text_summarization"
]

class SummarizerInterface(ABC):
    @abstractmethod
    def summarize(self, text: str, context: str = None) -> str:
        pass


class LocalSummarizer(SummarizerInterface):
    def __init__(self, model: str = HUGGINGFACE_SUMMARIZATION_MODELS[0]):
        self.summarizer = pipeline("summarization", model=model)

    def summarize(self, text: str, context: str = None) -> str:
        summary = self.summarizer(text, max_length=MAX_SUMMARY_LENGTH, min_length=100, do_sample=False)
        return summary[0]['summary_text']


class OpenAISummarizer(SummarizerInterface):
    def __init__(self, model: str = 'gpt-3.5-turbo'):
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        self.model = model
        self.last_response = None # debugging

    def _system_prompt() -> str:
        return (
            "You are a creative and experienced copywriter. "
            "You only use factual information and try not to add "
            "any new information when summarizing text. "
            "When summarizing text please try your best to keep the "
            "total length less than {MAX_SUMMARY_LENGTH} characters."
        )
    
    def _summarize_prompt(text_to_summarize: str) -> str:
        return (
            "Please write a summary of the "
            "following text using friendly, easy to read language:\n\n"
            "\"\"\""
            "{text_to_summarize}"
            "\"\"\""
        )
    
    def _summarize_with_context_prompt(text_to_summarize: str, context: str) -> str:
        return (
            "Please write a summary of the text marked SUMMARIZE paying particular "
            "attention to what is relevant to the text marked CONTEXT. "
            "Use friendly, easy to read language:\n\n"
            "CONTEXT:"
            "\"\"\""
            "{context}"
            "\"\"\""
            "\n\n"
            "SUMMARIZE:"
            "\"\"\""
            "{text_to_summarize}"
            "\"\"\""
        )

    def summarize(self, text: str, context: str = None) -> str:
        if context:
            prompt_text = self._summarize_with_context_prompt(text, context)
        else:
            prompt_text = self._summarize_prompt(text)

        self.last_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": prompt_text},
            ]
        ).model_dump()

        return self.last_response['choices'][0]['message']['content']

