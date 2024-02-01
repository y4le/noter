import os
from flask import Flask, request, render_template, redirect, url_for
from noter_gpt.database import VectorDatabaseInterface, get_database
from noter_gpt.embedder import EmbedderInterface, get_embedder
from noter_gpt.summarizer import SummarizerInterface, get_summarizer
from noter_gpt.searcher import SearcherInterface, get_searcher
from noter_gpt.storage import Storage

app = Flask(__name__)

storage: Storage = None
database: VectorDatabaseInterface = None
summarizer: SummarizerInterface = None
searcher: SearcherInterface = None


@app.route("/")
def index():
    notes = [note for note in storage.all_notes()]
    return render_template("index.html", notes=notes)


@app.route("/note/<path:filename>", methods=["GET", "POST"])
def note(filename):
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
def note_content(filename):
    filepath = storage.note_abs_path(filename)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            content = f.read()
        return content
    return f"Note for {filename} not found", 404


@app.route("/note-summary/<path:filename>")
def note_summary(filename):
    filepath = storage.note_abs_path(filename)
    if os.path.exists(filepath):
        return summarizer.summarize_file(filepath)
    return f"Note for {filename} not found", 404


@app.route("/text-summary", methods=["POST"])
def text_summary():
    data = request.get_json()
    text = data["text"]
    return summarizer.summarize_text(text)


@app.route("/search-full-text")
def search_full_text():
    query = request.args.get("query", "")
    if query:
        documents = searcher.text_search(query)
        return render_template("index.html", notes=documents, query=query)
    else:
        return redirect(url_for("index"))


def format_similar(content):
    # Rebuild or update the index after updating the note
    database.build_or_update_index()
    similar_notes = database.find_similar(content, n=5)
    formatted_similar_notes = [
        (name, f"{similarity:.3f}") for name, similarity in similar_notes
    ]
    return formatted_similar_notes


def run_server(use_openai=False):
    # Hacky nonsense to inject dependencies

    # Initialize Storage
    global storage
    storage = Storage()

    # Initialize the Documentdatabase and build the index
    global database
    database = get_database(
        storage=storage, embedder=get_embedder(use_openai=use_openai)
    )
    database.build_or_update_index()

    # Initialize the LocalSummarizer
    global summarizer
    summarizer = get_summarizer(storage=storage, use_openai=use_openai)

    # Initialize the Searcher
    global searcher
    searcher = get_searcher(storage=storage)

    app.run(debug=True, use_reloader=False, port=31337)


if __name__ == "__main__":
    run_server()
