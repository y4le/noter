import argparse
from typing import List, Tuple, Iterator

from noter_gpt.database.annoy_database import AnnoyDatabase
from noter_gpt.summarizer.inject import inject_summarizer
from noter_gpt.summarizer.batch_summarizer import BatchSummarizer
from noter_gpt.storage import Storage
from noter_gpt.server import run_server


def search_documents(
    query_file: str, n: int, storage: Storage
) -> List[Tuple[str, float]]:
    database = AnnoyDatabase(storage=storage)
    database.build_or_update_index()
    return database.find_similar_to_file(query_file, n)


def summarize_document(
    file_path: str, storage: Storage, use_openai: bool, model=None
) -> str:
    summarizer = inject_summarizer(
        storage=storage, use_openai=use_openai, model_name=model
    )
    return summarizer.summarize_file(file_path)


def stream_summarize_document(
    file_path: str, storage: Storage, use_openai: bool
) -> Iterator[str]:
    summarizer = inject_summarizer(storage=storage, use_openai=use_openai)
    return summarizer.stream_summarize_file(file_path)


def summarize_all(storage: Storage, use_openai: bool) -> None:
    summarizer = inject_summarizer(storage=storage, use_openai=use_openai)
    batch_summarizer = BatchSummarizer(summarizer, storage=storage)
    return batch_summarizer.parallel_summarize_all_notes()


def cli():
    parser = argparse.ArgumentParser(description="Noter app CLI")
    parser.add_argument(
        "command",
        choices=[
            "search",
            "summarize",
            "stream_summarize",
            "gemma_summarize",
            "mixtral_summarize",
            "summarize_all",
            "server",
        ],
    )
    parser.add_argument("directory_or_file", type=str, nargs="?", default=None)
    parser.add_argument(
        "--n", type=int, default=5, help="Number of similar documents to retrieve"
    )
    parser.add_argument(
        "--root-path", type=str, default=None, help="Root path for the storage"
    )
    parser.add_argument(
        "--cache-path", type=str, default=None, help="Cache path for the storage"
    )
    parser.add_argument(
        "--use-openai",
        action="store_true",
        default=False,
        help="Use OpenAI API",
    )
    args = parser.parse_args()

    storage = Storage(root_path=args.root_path, cache_path=args.cache_path)

    if args.command == "search":
        results = search_documents(args.directory_or_file, args.n, storage)
        print(results)
    elif args.command == "summarize":
        summary = summarize_document(
            args.directory_or_file, storage, use_openai=args.use_openai
        )
        print(summary)
    elif args.command == "mixtral_summarize":
        summary = summarize_document(
            args.directory_or_file, storage, use_openai=args.use_openai, model="mixtral"
        )
        print(summary)
    elif args.command == "gemma_summarize":
        summary = summarize_document(
            args.directory_or_file, storage, use_openai=args.use_openai, model="gemma"
        )
        print(summary)
    elif args.command == "stream_summarize":
        for output in stream_summarize_document(
            args.directory_or_file, storage, use_openai=args.use_openai
        ):
            print(output, end="")
    elif args.command == "summarize_all":
        summarize_all(storage, use_openai=args.use_openai)
    elif args.command == "server":
        run_server(use_openai=args.use_openai)


if __name__ == "__main__":
    cli()
