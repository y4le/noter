import pytest
from noter_gpt.embedder import TransformersEmbedder, OpenAIEmbedder
import numpy as np

def test_transformers_embedder():
    transformers_embedder = TransformersEmbedder()
    text = "This is a test document."
    embedding = transformers_embedder.embed_document(text)
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (768,)

@pytest.mark.skip(reason="temporarily disabled API usage reasons")
def test_openai_embedder():
    openai_embedder = OpenAIEmbedder('your_api_key')
    text = "This is a test document."
    embedding = openai_embedder.embed_document(text)
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (768,)
