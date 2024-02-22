import os
from typing import Tuple, List
from flask import Flask, request, render_template, redirect, url_for

from noter_gpt.database import VectorDatabaseInterface, get_database
from noter_gpt.embedder.inject import inject_embedder
from noter_gpt.searcher import SearcherInterface, get_searcher
from noter_gpt.storage import Storage
from noter_gpt.summarizer.inject import SummarizerInterface, inject_summarizer

app = Flask(__name__)

storage: Storage
database: VectorDatabaseInterface
summarizer: SummarizerInterface
searcher: SearcherInterface


@app.route("/")
def index() -> str:
    notes = [note for note in storage.all_notes()]
    return render_template("index.html", notes=notes)


@app.route("/note/<path:filename>", methods=["GET", "POST"])
def note(filename: str) -> str:
    if request.method == "POST":
        if "delete" in request.form:
            original_filepath = storage.note_abs_path(filename)
            if os.path.exists(original_filepath):
                os.remove(original_filepath)
                database.build_or_update_index()  # Update the index after deletion
            return redirect(url_for("index"))

        content = request.form["main_content"]
        new_filename = request.form.get("new_filename", filename)
        new_filepath = os.path.join(storage.root_path, new_filename)

        # Save or update the content
        with open(new_filepath, "w") as f:
            f.write(content)

        # If the filename has been changed, handle the renaming
        if new_filename != filename:
            original_filepath = os.path.join(storage.root_path, filename)
            if os.path.exists(original_filepath):
                os.remove(original_filepath)

        similar_notes = format_similar(content)

        return render_template(
            "note.html",
            content=content,
            filename=new_filename,
            similar_notes=similar_notes,
        )

    else:
        filepath = storage.note_abs_path(filename)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read()
        else:
            content = ""

        similar_notes = format_similar(content)

        return render_template(
            "note.html", content=content, filename=filename, similar_notes=similar_notes
        )


@app.route("/note-content/<path:filename>")
def note_content(filename: str) -> str:
    filepath = storage.note_abs_path(filename)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            content = f.read()
        return content
    return f"Note for {filename} not found", 404


@app.route("/note-summary/<path:filename>")
def note_summary(filename: str) -> str:
    filepath = storage.note_abs_path(filename)
    if os.path.exists(filepath):
        return summarizer.summarize_file(filepath)
    return f"Note for {filename} not found", 404


@app.route("/text-summary", methods=["POST"])
def text_summary() -> str:
    data = request.get_json()
    text = data["text"]
    return summarizer.summarize_text(text)


@app.route("/search-full-text")
def search_full_text() -> str:
    query = request.args.get("query", "")
    if query:
        documents = searcher.text_search(query)
        return render_template("index.html", notes=documents, query=query)
    else:
        return redirect(url_for("index"))


def format_similar(content: str) -> List[Tuple[str, str]]:
    # Rebuild or update the index after updating the note
    database.build_or_update_index()
    similar_notes = database.find_similar(content, n=5)
    formatted_similar_notes = [
        (name, f"{similarity:.3f}") for name, similarity in similar_notes
    ]
    return formatted_similar_notes


def run_server(use_openai: bool = False) -> None:
    # Hacky nonsense to inject dependencies

    # Initialize Storage
    global storage
    storage = Storage()

    # Initialize the Documentdatabase and build the index
    global database
    database = get_database(
        storage=storage, embedder=inject_embedder(use_openai=use_openai)
    )
    database.build_or_update_index()

    # Initialize the LocalSummarizer
    global summarizer
    summarizer = inject_summarizer(storage=storage, use_openai=use_openai)

    # Initialize the Searcher
    global searcher
    searcher = get_searcher(storage=storage)

    app.run(debug=True, use_reloader=False, port=31337)


if __name__ == "__main__":
    run_server()
