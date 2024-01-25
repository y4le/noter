import argparse
from noter_gpt.database import AnnoyDatabase
from noter_gpt.summarizer import LocalSummarizer

def index_documents(directory, index_file):
    database = AnnoyDatabase(index_file=index_file)
    database.build_or_update_index(directory)

def search_documents(query_file, n, index_file):
    database = AnnoyDatabase(index_file=index_file)
    database.load_index()

    with open(query_file, 'r', encoding='utf-8') as file:
        query_text = file.read()

    return database.find_similar(query_text, n)

def summarize_document(file_path):
    summarizer = LocalSummarizer()
    return summarizer.summarize_file(file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Document database CLI")
    parser.add_argument("command", choices=["index", "search", "summarize"])
    parser.add_argument("directory_or_file")
    parser.add_argument("--n", type=int, default=5, help="Number of similar documents to retrieve")
    parser.add_argument("--index_file", default="index.ann", help="Filepath for saving/loading the index")
    args = parser.parse_args()

    if args.command == "index":
        index_documents(args.directory_or_file, args.index_file)
    elif args.command == "search":
        results = search_documents(args.directory_or_file, args.n, args.index_file)
        print(results)
    elif args.command == "summarize":
        summary = summarize_document(args.directory_or_file)
        print(summary)
