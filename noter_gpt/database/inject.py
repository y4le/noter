from noter_gpt.storage import Storage
from noter_gpt.embedder.interface import EmbedderInterface
from noter_gpt.database.interface import VectorDatabaseInterface
from noter_gpt.database.annoy_database import AnnoyDatabase


def inject_database(
    storage: Storage, embedder: EmbedderInterface
) -> VectorDatabaseInterface:
    return AnnoyDatabase(storage=storage, embedder=embedder)
