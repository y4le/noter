from transformers import AutoTokenizer, AutoModel
import torch
from annoy import AnnoyIndex
import os
import glob
import json
import hashlib

class DocumentEmbedder:
    def __init__(self, model_name="bert-base-uncased", index_file='index.ann'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.index = AnnoyIndex(768, 'angular')  # Dimension for BERT base
        self.index_file = index_file
        self.documents = {}  # Stores file paths and hashes
        self.index_to_path = {}  # Reverse mapping from index to file path

    def embed_document(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

    def build_index(self, directory):
        try:
            with open('file_hashes.json', 'r') as f:
                self.documents = json.load(f)
        except FileNotFoundError:
            self.documents = {}

        all_file_paths = glob.glob(os.path.join(directory, "*.txt"))
        for file_path in all_file_paths:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()

            doc_hash = hashlib.md5(text.encode('utf-8')).hexdigest()

            if file_path not in self.documents or self.documents[file_path]['hash'] != doc_hash:
                embedding = self.embed_document(text)
                index = len(self.documents)
                self.index.add_item(index, embedding)
                self.documents[file_path] = {'hash': doc_hash, 'index': index}
                self.index_to_path[index] = file_path  # Update reverse mapping

        # Remove documents that no longer exist
        self.documents = {fp: v for fp, v in self.documents.items() if fp in all_file_paths}
        self.index_to_path = {v['index']: fp for fp, v in self.documents.items()}

        self.index.build(10)
        self.index.save(self.index_file)

        with open('file_hashes.json', 'w') as f:
            json.dump(self.documents, f)

    def load_index(self):
        self.index.load(self.index_file)
        with open('file_hashes.json', 'r') as f:
            self.documents = json.load(f)
        self.index_to_path = {v['index']: fp for fp, v in self.documents.items()}

    def find_similar(self, query_text, n=5):
        query_embedding = self.embed_document(query_text)
        indices, distances = self.index.get_nns_by_vector(query_embedding, n, include_distances=True)
        return [(self.index_to_path[i], 1/(1 + d)) for i, d in zip(indices, distances)]
