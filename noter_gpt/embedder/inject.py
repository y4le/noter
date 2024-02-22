from noter_gpt.embedder.interface import EmbedderInterface
from noter_gpt.embedder.transformers_embedder import TransformersEmbedder
from noter_gpt.embedder.openai_embedder import OpenAIEmbedder


def inject_embedder(use_openai: bool = False) -> EmbedderInterface:
    if use_openai:
        return OpenAIEmbedder()
    return TransformersEmbedder()
