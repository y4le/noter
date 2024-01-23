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
    filepath = os.path.join(NOTES_DIRECTORY, filename)
    similar_notes = []
    if request.method == 'POST':
        content = request.form['content']
        with open(filepath, 'w') as f:
            f.write(content)

        # Rebuild the index after updating the note
        embedder.build_or_update_index(NOTES_DIRECTORY)

        # If 'Find Similar' button is clicked
        if 'find_similar' in request.form:
            similar_notes = embedder.find_similar(content, n=5)

        return render_template('note.html', content=content, filename=filename, similar_notes=similar_notes)

    else:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
        else:
            content = ''
        return render_template('note.html', content=content, filename=filename, similar_notes=similar_notes)

if __name__ == '__main__':
    app.run(debug=True)
