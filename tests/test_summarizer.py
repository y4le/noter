import pytest
from noter_gpt.summarizer import LocalSummarizer, OpenAISummarizer

def test_local_summarizer(shared_datadir):
    summarizer = LocalSummarizer()
    file_path = shared_datadir / 'notes' / 'car.txt'
    with open(file_path, 'r') as f:
        original_text = f.read()
    summary = summarizer.summarize_file(file_path)
    assert isinstance(summary, str)
    assert len(summary) < len(original_text)

@pytest.mark.skip(reason="temporarily disabled API usage reasons")
def test_openai_summarizer(shared_datadir):
    summarizer = OpenAISummarizer()
    file_path = shared_datadir / 'notes' / 'car.txt'
    with open(file_path, 'r') as f:
        original_text = f.read()
    summary = summarizer.summarize_file(file_path)
    assert isinstance(summary, str)
    assert len(summary) < len(original_text)

def test_local_summarizer_cache(shared_datadir):
    summarizer = LocalSummarizer()
    file_path = shared_datadir / 'notes' / 'car.txt'
    summary1 = summarizer.summarize_file(file_path)
    summary2 = summarizer.summarize_file(file_path)
    assert summary1 == summary2

@pytest.mark.skip(reason="temporarily disabled API usage reasons")
def test_openai_summarizer_cache(shared_datadir):
    summarizer = OpenAISummarizer()
    file_path = shared_datadir / 'notes' / 'car.txt'
    summary1 = summarizer.summarize_file(file_path)
    summary2 = summarizer.summarize_file(file_path)
    assert summary1 == summary2
