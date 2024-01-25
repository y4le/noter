import pytest
from noter_gpt.database import AnnoyDatabase
from noter_gpt.embedder import TransformersEmbedder
import numpy as np
import os
import json
import tempfile

@pytest.fixture
def embedder():
    return TransformersEmbedder()

@pytest.fixture
def database(embedder):
    return AnnoyDatabase(embedder=embedder)

@pytest.fixture
def notes_directory(tmp_path):
    notes_dir = tmp_path / 'notes'
    notes_dir.mkdir()

    dog_file_path = notes_dir / 'dog.txt'
    cat_file_path = notes_dir / 'cat.txt'
    car_file_path = notes_dir / 'car.txt'
    airplane_file_path = notes_dir / 'airplane.txt'

    dog_content = (
        "Dogs are known as man's best friend. They are loyal and protective. "
        "They come in a variety of breeds, each with its own unique characteristics."
    )
    cat_content = (
        "Cats are often kept as pets for their companionship and ability to hunt vermin. "
        "They are known for their independence and agility."
    )
    car_content = (
        "Cars have revolutionized transportation, allowing for personal mobility and freedom to "
        "travel. They come in various models, each designed for specific needs, from compact city "
        "cars to rugged off-road vehicles."
    )
    airplane_content = (
        "Airplanes are a fast and efficient mode of transportation, enabling long-distance travel "
        "across continents and oceans. They are crucial for international commerce and tourism. "
        "From small private aircraft to large commercial jets, airplanes come in various sizes and "
        "capacities."
    )

    dog_file_path.write_text(dog_content)
    cat_file_path.write_text(cat_content)
    car_file_path.write_text(car_content)
    airplane_file_path.write_text(airplane_content)

    return notes_dir

def test_build_or_update_index(database):
    # Create a temporary directory and file for testing
    with tempfile.TemporaryDirectory() as tmpdirname:
        test_file_path = os.path.join(tmpdirname, 'test.txt')
        with open(test_file_path, 'w') as f:
            f.write('test text')

        database.build_or_update_index(tmpdirname)
        assert not database.need_rebuild
        assert test_file_path in database.documents

def test_find_similar_finds_actually_similar(database, notes_directory):
    # Index the contents of the notes directory
    database.build_or_update_index(str(notes_directory))

    # Search for 'cat.txt' content and check that 'dog.txt' is the first result
    cat_file_path = notes_directory / 'cat.txt'
    cat_content = cat_file_path.read_text()
    search_results = database.find_similar(cat_content)
    assert search_results[0][0] == 'dog.txt', "Expected 'dog.txt' to be the first search result."

def test_find_similar_respects_n(database, notes_directory):
    # Index the contents of the notes directory
    database.build_or_update_index(str(notes_directory))

    # Search for 'cat.txt' content and check that 'dog.txt' is the first result
    cat_file_path = notes_directory / 'cat.txt'
    cat_content = cat_file_path.read_text()
    search_results = database.find_similar(cat_content, n=1)
    assert len(search_results) == 1
