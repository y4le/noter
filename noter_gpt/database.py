import hashlib
import json
import os
from abc import ABC, abstractmethod
from typing import List, Tuple
from functools import cached_property

from annoy import AnnoyIndex

from noter_gpt.storage import Storage
from noter_gpt.embedder import EmbedderInterface, TransformersEmbedder


class VectorDatabaseInterface(ABC):
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
        pass

    @abstractmethod
    def rebuild_index(self) -> None:
        pass

    @abstractmethod
    def find_similar(self, query_text: str, n: int = 5) -> List[Tuple[str, float]]:
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
        pass


class AnnoyDatabase(VectorDatabaseInterface):
    def __init__(
        self,
        storage: Storage = None,
        embedder: EmbedderInterface = None,
    ):
        super().__init__(storage=storage)
        if not embedder:
            self.embedder = TransformersEmbedder()
        else:
            self.embedder = embedder
        self.index = AnnoyIndex(self.embedder.dimension(), "angular")
        self.index_file = self.storage.built_index_file(self.embedder.identifier)
        self.item_count = 0  # Counter for the number of items in the index

    def get_embedding(self, text: str) -> List[float]:
        return self.embedder.embed_text(text).tolist()

    def rebuild_index(self) -> None:
        self.index = AnnoyIndex(self.embedder.dimension(), "angular")
        self.item_count = 0  # Reset the counter
        for doc in self.documents.values():
            self.index.add_item(self.item_count, doc["embedding"])
            self.item_count += 1  # Increment the counter for each item
        self.index.build(20)
        self.index.save(self.index_file)
        self.need_rebuild = False

    def _load_documents(self) -> None:
        super()._load_documents()
        if os.path.exists(self.index_file):
            self.index.load(self.index_file)

    def find_similar(self, query_text: str, n: int = 5) -> List[Tuple[str, float]]:
        if not query_text:
            return []

        if self.need_rebuild:
            self.rebuild_index()

        query_embedding = self.embedder.embed_text(query_text)
        indices, distances = self.index.get_nns_by_vector(
            query_embedding, n + 1, include_distances=True
        )
        similar_files = [
            (list(self.documents)[i], 1 / (1 + d)) for i, d in zip(indices, distances)
        ]
        return similar_files[1:]  # exclude self

    def find_similar_to_file(self, path: str, n: int = 5) -> List[Tuple[str, float]]:
        return super().find_similar_to_file(path, n)

    @cached_property
    def embedding_cache_file(self) -> str:
        return self.storage.embedding_cache_file(self.embedder.identifier)


def get_database(storage: Storage, embedder: EmbedderInterface):
    return AnnoyDatabase(storage=storage, embedder=embedder)
