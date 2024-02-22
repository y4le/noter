import os
from functools import cached_property

import numpy as np
from openai import OpenAI

from noter_gpt.embedder.interface import EmbedderInterface


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
