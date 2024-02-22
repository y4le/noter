import os
from typing import List


def relativize_paths(paths: List[str], root_path: str) -> List[str]:
    return [os.path.relpath(path, root_path) for path in paths]
