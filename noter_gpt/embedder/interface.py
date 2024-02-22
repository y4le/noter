from abc import ABC, abstractmethod
from functools import cached_property

import numpy as np


class EmbedderInterface(ABC):
    """Creates a vector representation of a given text or file"""

    @abstractmethod
    def embed_text(self, text: str) -> np.ndarray:
        """Should return a vector representation of the given text"""
        pass

    @abstractmethod
    def embed_file(self, file_path: str) -> np.ndarray:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        return self.embed_text(text)

    @abstractmethod
    def dimension(self) -> int:
        """Should return the dimension of the embeddings produced by this class"""
        pass

    @cached_property
    @abstractmethod
    def identifier(self) -> str:
        """Should return a unique ID that is used to cache results of this embedder"""
        pass
