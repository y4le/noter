import argparse
from typing import List, Tuple
from noter_gpt.database import AnnoyDatabase
from noter_gpt.summarizer import LocalSummarizer


def index_documents(directory: str, cache_dir: str) -> None:
    database = AnnoyDatabase(cache_dir=cache_dir)
    database.build_or_update_index(directory)


def search_documents(
    query_file: str, n: int, cache_dir: str
) -> List[Tuple[str, float]]:
    database = AnnoyDatabase(cache_dir=cache_dir)
    database._load_documents()

    with open(query_file, "r", encoding="utf-8") as file:
        query_text = file.read()

    return database.find_similar(query_text, n)


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
        "--cache_dir",
        default=".noter/",
        help="Filepath for saving/loading caches",
    )
    args = parser.parse_args()

    if args.command == "index":
        index_documents(args.directory_or_file, args.cache_dir)
    elif args.command == "search":
        results = search_documents(args.directory_or_file, args.n, args.cache_dir)
        print(results)
    elif args.command == "summarize":
        summary = summarize_document(args.directory_or_file)
        print(summary)
