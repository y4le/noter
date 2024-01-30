import os
from typing import List

DEFAULT_CACHE_DIR = ".notes/"


class Storage:
    def __init__(self, root_path: str = None, cache_path: str = None):
        self._init_root_path(root_path)
        self._init_cache_path(cache_path)
        os.chdir(self.root_path)

    def _init_root_path(self, root_path: str) -> None:
        self.root_path = root_path
        if not self.root_path:
            self.root_path = os.environ.get("NOTER_NOTES_DIR")

        self.root_path = os.path.expanduser(self.root_path)

        if not self.root_path:
            raise AssertionError("No root path set")
        if not os.path.exists(self.root_path):
            raise AssertionError(f"Root path '{self.root_path}' does not exist")

    def _init_cache_path(self, cache_path: str) -> None:
        self.cache_path = cache_path
        if not self.cache_path:
            self.cache_path = os.environ.get("NOTER_CACHE_DIR")
        if not self.cache_path:
            self.cache_path = os.path.join(self.root_path, DEFAULT_CACHE_DIR)

        self.cache_path = os.path.expanduser(self.cache_path)

        os.makedirs(self.cache_path, exist_ok=True)

    def embedding_cache_file(self) -> str:
        return os.path.join(self.cache_path, "embedding_hashes.json")

    def built_index_file(self) -> str:
        return os.path.join(self.cache_path, "index.ann")

    def summary_cache_file(self) -> str:
        return os.path.join(self.cache_path, "file_summaries.json")

    def all_notes(self) -> List[str]:
        all_note_paths = []
        for root, dirs, notes in os.walk(self.root_path):
            notes = [
                os.path.join(root, f)
                for f in notes
                if not f[0] == "." and f.endswith(".txt")
            ]
            dirs[:] = [d for d in dirs if not d[0] == "."]
            for note in notes:
                relative_path = os.path.relpath(note, self.root_path)
                all_note_paths.append(relative_path)
        return sorted(all_note_paths)

    def note_abs_path(self, note: str) -> str:
        return os.path.join(self.root_path, note)
