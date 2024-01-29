import glob
import hashlib
import json
import os
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Tuple

from annoy import AnnoyIndex

from noter_gpt.embedder import EmbedderInterface, TransformersEmbedder


class VectorDatabaseInterface(ABC):
    def __init__(self, cache_dir: str = ".noter"):
        self.cache_dir = cache_dir
        self.hash_cache_path = (Path(cache_dir) / "file_hashes.json").as_posix()
        self.documents = {}  # Stores file paths, hashes, and embeddings
        self.need_rebuild = True  # Flag to check if rebuild is required

    def _load_documents(self) -> None:
        try:
            with open(self.hash_cache_path, "r") as f:
                self.documents = json.load(f)
        except FileNotFoundError:
            self.documents = {}

    def _save_documents(self) -> None:
        os.makedirs(os.path.dirname(self.hash_cache_path), exist_ok=True)
        with open(self.hash_cache_path, "w+") as f:
            json.dump(self.documents, f)

    def build_or_update_index(self, directory: str) -> None:
        self._load_documents()

        all_file_paths = []
        for root, dirs, files in os.walk(directory):
            files = [f for f in files if not f[0] == '.' and f.endswith('.txt')]
            dirs[:] = [d for d in dirs if not d[0] == '.']
            for file in files:
                all_file_paths.append(file)

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


class AnnoyDatabase(VectorDatabaseInterface):
    def __init__(self, embedder: EmbedderInterface = None, cache_dir: str = ".noter"):
        super().__init__()
        if not embedder:
            self.embedder = TransformersEmbedder()
        else:
            self.embedder = embedder
        self.index = AnnoyIndex(768, "angular")  # Dimension for BERT base
        self.index_file = (Path(self.cache_dir) / "index.ann").as_posix()
        self.item_count = 0  # Counter for the number of items in the index

    def get_embedding(self, text: str) -> List[float]:
        return self.embedder.embed_text(text).tolist()

    def rebuild_index(self) -> None:
        self.index = AnnoyIndex(768, "angular")
        self.item_count = 0  # Reset the counter
        for doc in self.documents.values():
            self.index.add_item(self.item_count, doc["embedding"])
            self.item_count += 1  # Increment the counter for each item
        self.index.build(20)
        os.makedirs(self.cache_dir, exist_ok=True)
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
            (os.path.basename(list(self.documents)[i]), 1 / (1 + d))
            for i, d in zip(indices, distances)
        ]
        return similar_files[1:]  # exclude self
