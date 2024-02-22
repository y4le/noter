from functools import cached_property

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

from noter_gpt.embedder.interface import EmbedderInterface


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
