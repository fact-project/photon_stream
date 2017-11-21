from . import io
import gzip
import pandas as pd


class EventListReader:
    """
    An EventListReader() reads Events() from a file.
    The Events are sequentially loaded from the file as needed.
    """
    def __init__(self, path):
        """
        Load FACT observations from a file.
        """
        self.path = path
        self.gzipped = io.is_gzipped_file(path)
        if self.gzipped:
            with gzip.open(path, 'rb') as fin:
                if io.binary.is_phs_binary(fin):
                    self.file = gzip.open(path, 'rb')
                    self.reader = io.binary.Reader(self.file)
                else:
                    self.file = gzip.open(path, 'rt')
                    self.reader = io.jsonl.Reader(self.file)
        else:
            with open(path, 'rb') as fin:
                if io.binary.is_phs_binary(fin):
                    self.file = open(path, 'rb')
                    self.reader = io.binary.Reader(self.file)
                else:
                    self.file = open(path, 'rt')
                    self.reader = io.jsonl.Reader(self.file)
          

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.file.close()

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.reader)

    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += "path '" + self.path + "'"
        out += ')\n'
        return out
