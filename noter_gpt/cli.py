import argparse
from typing import List, Tuple
from noter_gpt.database import AnnoyDatabase
from noter_gpt.summarizer import LocalSummarizer
from noter_gpt.storage import Storage


def search_documents(
    query_file: str, n: int, storage: Storage
) -> List[Tuple[str, float]]:
    database = AnnoyDatabase(storage=storage)
    database.build_or_update_index()
    return database.find_similar_to_file(query_file, n)


def summarize_document(file_path: str) -> str:
    summarizer = LocalSummarizer()
    return summarizer.summarize_file(file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Document database CLI")
    parser.add_argument("command", choices=["index", "search", "summarize"])
    parser.add_argument("directory_or_file")
    parser.add_argument(
        "--n", type=int, default=5, help="Number of similar documents to retrieve"
    )
    parser.add_argument(
        "--root-path", type=str, default=None, help="Root path for the storage"
    )
    parser.add_argument(
        "--cache-path", type=str, default=None, help="Cache path for the storage"
    )
    args = parser.parse_args()

    storage = Storage(root_path=args.root_path, cache_path=args.cache_path)

    if args.command == "search":
        results = search_documents(args.directory_or_file, args.n, storage)
        print(results)
    elif args.command == "summarize":
        summary = summarize_document(args.directory_or_file)
        print(summary)
