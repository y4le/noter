import os
from abc import ABC, abstractmethod
import numpy as np

from transformers import AutoTokenizer, AutoModel
import torch
from openai import OpenAI

class EmbedderInterface(ABC):
    @abstractmethod
    def embed_document(self, text: str) -> np.ndarray:
        pass


class TransformersEmbedder(EmbedderInterface):
    def __init__(self, model_name: str = "bert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def embed_document(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()


class OpenAIEmbedder(EmbedderInterface):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

    def embed_document(self, text: str, model: str = "text-embedding-ada-002") -> np.ndarray:
        text = text.replace("\n", " ")
        return self.client.embeddings.create(input = [text], model=model).data[0].embedding