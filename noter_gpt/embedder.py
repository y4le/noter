import os
from abc import ABC, abstractmethod
import numpy as np

from transformers import AutoTokenizer, AutoModel
import torch
from openai import OpenAI


class EmbedderInterface(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> np.ndarray:
        pass

    @abstractmethod
    def embed_file(self, file_path: str) -> np.ndarray:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        return self.embed_text(text)

    @abstractmethod
    def dimension(self) -> int:
        pass


class TransformersEmbedder(EmbedderInterface):
    def __init__(self, model_name: str = "bert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def embed_text(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

    def embed_file(self, file_path: str) -> np.ndarray:
        return super().embed_file(file_path)

    def dimension(self):
        return self.model.config.hidden_size


class OpenAIEmbedder(EmbedderInterface):
    def __init__(self):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def embed_text(
        self, text: str, model: str = "text-embedding-ada-002"
    ) -> np.ndarray:
        text = text.replace("\n", " ")
        return np.array(
            self.client.embeddings.create(input=[text], model=model).data[0].embedding
        )

    def embed_file(self, file_path: str) -> np.ndarray:
        return super().embed_file(file_path)

    def dimension(self):
        return 1536
