import pytest
from noter_gpt.embedder import TransformersEmbedder, OpenAIEmbedder
import numpy as np


def test_transformers_embedder(shared_datadir):
    transformers_embedder = TransformersEmbedder()
    file_path = shared_datadir / "notes" / "animals" / "cat.txt"
    embedding = transformers_embedder.embed_file(file_path)
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (transformers_embedder.dimension(),)


@pytest.mark.api
def test_openai_embedder(shared_datadir):
    openai_embedder = OpenAIEmbedder()
    file_path = shared_datadir / "notes" / "animal" / "cat.txt"
    embedding = openai_embedder.embed_file(file_path)
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (openai_embedder.dimension(),)
