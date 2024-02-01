import os
from abc import ABC, abstractmethod
from functools import cached_property

import numpy as np
import torch
from openai import OpenAI
from transformers import AutoModel, AutoTokenizer


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
        # return the dimension of the embeddings produced by this class
        pass

    @cached_property
    @abstractmethod
    def identifier(self) -> str:
        # return a unique ID that is used to cache results of this embedder
        pass


class TransformersEmbedder(EmbedderInterface):
    def __init__(self, model_name: str = "bert-base-uncased"):
        self.model_name = model_name
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

    @cached_property
    def identifier(self) -> str:
        f"TransformersEmbedder_{self.model_name}"


class OpenAIEmbedder(EmbedderInterface):
    def __init__(self, model_name: str = "text-embedding-ada-002"):
        self.model_name = model_name
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def embed_text(self, text: str) -> np.ndarray:
        text = text.replace("\n", " ")
        return np.array(
            self.client.embeddings.create(input=[text], model=self.model_name)
            .data[0]
            .embedding
        )

    def embed_file(self, file_path: str) -> np.ndarray:
        return super().embed_file(file_path)

    def dimension(self):
        return 1536

    @cached_property
    def identifier(self) -> str:
        return f"OpenAiEmbedder_{self.model_name}"


def get_embedder(use_openai: bool = False) -> EmbedderInterface:
    if use_openai:
        return OpenAIEmbedder()
    return TransformersEmbedder()
