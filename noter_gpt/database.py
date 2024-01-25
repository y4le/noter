import glob
import hashlib
import json
import os
from abc import ABC, abstractmethod
from typing import List, Tuple

from annoy import AnnoyIndex

from noter_gpt.embedder import EmbedderInterface, TransformersEmbedder

HASH_CACHE_PATH = '.noter/file_hashes.json'

class VectorDatabaseInterface(ABC):
    def __init__(self):
        self.documents = {}  # Stores file paths, hashes, and embeddings
        self.need_rebuild = True  # Flag to check if rebuild is required

    def _load_documents(self) -> None:
        try:
            with open(HASH_CACHE_PATH, 'r') as f:
                self.documents = json.load(f)
        except FileNotFoundError:
            self.documents = {}

    def _save_documents(self) -> None:
        os.makedirs(os.path.dirname(HASH_CACHE_PATH), exist_ok=True)
        with open(HASH_CACHE_PATH, 'w+') as f:
            json.dump(self.documents, f)

    def build_or_update_index(self, directory: str) -> None:
        self._load_documents()

        all_file_paths = glob.glob(os.path.join(directory, "*.txt"))
        for file_path in all_file_paths:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()

            doc_hash = hashlib.md5(text.encode('utf-8')).hexdigest()

            if file_path not in self.documents or self.documents[file_path]['hash'] != doc_hash:
                embedding = self.get_embedding(text)
                self.documents[file_path] = {'hash': doc_hash, 'embedding': embedding}
                self.need_rebuild = True

        # Remove documents that no longer exist
        self.documents = {fp: v for fp, v in self.documents.items() if fp in all_file_paths}

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
    def __init__(self, embedder: EmbedderInterface = None, index_file: str = '.noter/index.ann'):
        super().__init__()
        if not embedder:
            self.embedder = TransformersEmbedder()
        else:
            self.embedder = embedder
        self.index = AnnoyIndex(768, 'angular')  # Dimension for BERT base
        self.index_file = index_file
        self.item_count = 0  # Counter for the number of items in the index

    def get_embedding(self, text: str) -> List[float]:
        return self.embedder.embed_document(text).tolist()

    def rebuild_index(self) -> None:
        self.index = AnnoyIndex(768, 'angular')
        self.item_count = 0  # Reset the counter
        for doc in self.documents.values():
            self.index.add_item(self.item_count, doc['embedding'])
            self.item_count += 1  # Increment the counter for each item
        self.index.build(20)
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        self.index.save(self.index_file)
        self.need_rebuild = False

    def load_index(self) -> None:
        self.index.load(self.index_file)
        with open(HASH_CACHE_PATH, 'r') as f:
            self.documents = json.load(f)

    def find_similar(self, query_text: str, n: int = 5) -> List[Tuple[str, float]]:
        if not query_text:
            return []

        if self.need_rebuild:
            self.rebuild_index()

        query_embedding = self.embedder.embed_document(query_text)
        indices, distances = self.index.get_nns_by_vector(query_embedding, n+1, include_distances=True)
        similar_files = [(os.path.basename(list(self.documents)[i]), 1/(1 + d)) for i, d in zip(indices, distances)]
        return similar_files[1:] # exclude self
