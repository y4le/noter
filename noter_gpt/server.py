from flask import Flask, request, render_template, redirect, url_for
from document_embedder import DocumentEmbedder  # Import the DocumentEmbedder class
import os

app = Flask(__name__)
NOTES_DIRECTORY = 'notes'
INDEX_FILE = 'index.ann'  # File for the Annoy index

# Ensure the notes directory exists
os.makedirs(NOTES_DIRECTORY, exist_ok=True)

# Initialize the DocumentEmbedder and build the index
embedder = DocumentEmbedder(index_file=INDEX_FILE)
embedder.build_or_update_index(NOTES_DIRECTORY)

@app.route('/')
def index():
    notes = os.listdir(NOTES_DIRECTORY)
    return render_template('index.html', notes=notes)

@app.route('/note/<filename>', methods=['GET', 'POST'])
def note(filename):
    if request.method == 'POST':
        content = request.form['content']
        new_filename = request.form.get('new_filename', filename)
        new_filepath = os.path.join(NOTES_DIRECTORY, new_filename)

        # Save or update the content
        with open(new_filepath, 'w') as f:
            f.write(content)

        # If the filename has been changed, handle the renaming
        if new_filename != filename:
            original_filepath = os.path.join(NOTES_DIRECTORY, filename)
            if os.path.exists(original_filepath):
                os.remove(original_filepath)

        # Rebuild or update the index after updating the note
        embedder.build_or_update_index(NOTES_DIRECTORY)

        if 'find_similar' in request.form:
            similar_notes = embedder.find_similar(content, n=5)
        else:
            similar_notes = []

        return render_template('note.html', content=content, filename=new_filename, similar_notes=similar_notes)

    else:
        filepath = os.path.join(NOTES_DIRECTORY, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
        else:
            content = ''
        return render_template('note.html', content=content, filename=filename, similar_notes=[])

@app.route('/note-content/<filename>')
def note_content(filename):
    filepath = os.path.join(NOTES_DIRECTORY, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        return content
    return "Note not found", 404

if __name__ == '__main__':
    app.run(debug=True)
