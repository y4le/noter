from multiprocessing.pool import ThreadPool

from tqdm import tqdm

from noter_gpt.storage import Storage
from noter_gpt.summarizer import SummarizerInterface


class BatchSummarizer:
    def __init__(self, summarizer: SummarizerInterface, storage: Storage = None):
        self.summarizer = summarizer

        self.storage = storage
        if not self.storage:
            self.storage = Storage()

    def summarize_all_notes(self):
        for file in tqdm(self.storage.all_notes()):
            self.summarizer.summarize_file(file)

    def parallel_summarize_all_notes(self):
        def worker(note):
            return self.summarizer.summarize_file(note)

        pool = ThreadPool()
        notes = list(self.storage.all_notes())
        for _ in tqdm(pool.imap(worker, notes), total=len(notes)):
            pass
        pool.close()
        pool.join()
