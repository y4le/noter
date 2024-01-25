import pytest
import os
from noter_gpt.cli import index_documents, search_documents

def test_index_documents(tmpdir):
    # Create a temporary directory and file for testing
    test_file_path = os.path.join(tmpdir, 'test.txt')
    with open(test_file_path, 'w') as f:
        f.write('test text')

    index_file = os.path.join(tmpdir, 'index.ann')
    index_documents(tmpdir, index_file)

    assert os.path.exists(index_file)

def test_search_documents_excludes_self(tmpdir):
    # Create a temporary directory and file for testing
    test_file_path = os.path.join(tmpdir, 'test.txt')
    with open(test_file_path, 'w') as f:
        f.write('test text')

    index_file = os.path.join(tmpdir, 'index.ann')
    index_documents(tmpdir, index_file)

    results = search_documents(test_file_path, 1, index_file)
    assert len(results) == 0

def test_search_documents(tmpdir):
    # Create a temporary directory and file for testing
    test_file_path_1_suffix = 'test1.txt'
    test_file_path_1 = os.path.join(tmpdir, test_file_path_1_suffix)
    with open(test_file_path_1, 'w') as f:
        f.write('test text 1')

    test_file_path_2 = os.path.join(tmpdir, 'test2.txt')
    with open(test_file_path_2, 'w') as f:
        f.write('test text 2')

    index_file = os.path.join(tmpdir, 'index.ann')
    index_documents(tmpdir, index_file)

    results = search_documents(test_file_path_2, 1, index_file)
    assert len(results) == 1
    assert results[0][0] == test_file_path_1_suffix

