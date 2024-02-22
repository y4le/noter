from multiprocessing.pool import ThreadPool

from tqdm import tqdm

from noter_gpt.storage import Storage
from noter_gpt.summarizer.interface import SummarizerInterface


class BatchSummarizer:
    def __init__(self, summarizer: SummarizerInterface, storage: Storage = None):
        self.summarizer = summarizer
        self.storage = storage if storage else Storage()

    def summarize_all_notes(self) -> None:
        for file in tqdm(self.storage.all_notes()):
            self.summarizer.summarize_file(file)

    def parallel_summarize_all_notes(self) -> None:
        def worker(note):
            return self.summarizer.summarize_file(note)

        with ThreadPool() as pool:
            notes = list(self.storage.all_notes())
            for _ in tqdm(pool.imap(worker, notes), total=len(notes)):
                pass
