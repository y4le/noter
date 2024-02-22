import os
from typing import List, Tuple
from functools import cached_property

from annoy import AnnoyIndex

from noter_gpt.embedder.interface import EmbedderInterface
from noter_gpt.embedder.transformers_embedder import TransformersEmbedder
from noter_gpt.storage import Storage
from noter_gpt.database.interface import VectorDatabaseInterface


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
