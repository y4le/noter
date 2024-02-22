import os
import hashlib
import json
from abc import ABC, abstractmethod
from typing import List, Tuple
from functools import cached_property

from noter_gpt.storage import Storage


class VectorDatabaseInterface(ABC):
    """Stores vectors and allows retrieval by similarity"""

    def __init__(self, storage: Storage = None):
        self.storage = storage
        if not self.storage:
            self.storage = Storage()
        self.documents = {}  # Stores file paths, hashes, and embeddings
        self.need_rebuild = True  # Flag to check if rebuild is required

    def _load_documents(self) -> None:
        try:
            with open(self.embedding_cache_file, "r") as f:
                self.documents = json.load(f)
        except FileNotFoundError:
            self.documents = {}

    def _save_documents(self) -> None:
        with open(self.embedding_cache_file, "w+") as f:
            json.dump(self.documents, f)

    def build_or_update_index(self) -> None:
        self._load_documents()

        all_file_paths = self.storage.all_notes()

        for file_path in all_file_paths:
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()

            doc_hash = hashlib.md5(text.encode("utf-8")).hexdigest()

            if (
                file_path not in self.documents
                or self.documents[file_path]["hash"] != doc_hash
            ):
                embedding = self.get_embedding(text)
                self.documents[file_path] = {"hash": doc_hash, "embedding": embedding}
                self.need_rebuild = True

        # Remove documents that no longer exist
        self.documents = {
            fp: v for fp, v in self.documents.items() if fp in all_file_paths
        }

        if self.need_rebuild:
            self.rebuild_index()

        self._save_documents()

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Should return the embedding of the given text"""
        pass

    @abstractmethod
    def rebuild_index(self) -> None:
        """Rebuilds the index from the documents"""
        pass

    @abstractmethod
    def find_similar(self, query_text: str, n: int = 5) -> List[Tuple[str, float]]:
        """Finds the n most similar documents to the given text"""
        pass

    @abstractmethod
    def find_similar_to_file(self, path: str, n: int = 5) -> List[Tuple[str, float]]:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as file:
            file_contents = file.read()
        return self.find_similar(file_contents, n)

    @cached_property
    @abstractmethod
    def embedding_cache_file(self) -> str:
        """Should return the path to the file where the embeddings are cached"""
        pass
