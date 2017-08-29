import ujson as json
import os
import gzip
from .is_gzipped_file import is_gzipped_file

class JsonLinesReader:
    """
    Sequentially reads a JSON-Lines file line by line and provides
    dictionaries for each line. Also supports gzipped files.
    """
    def __init__(self, path):
        self.path = os.path.abspath(path)

        if is_gzipped_file(path):
            self.file = gzip.open(path, 'rt')
        else:
            self.file = open(path, 'rt')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.file.close()

    def __iter__(self):
        return self

    def __next__(self):
        line = self.file.readline().strip().rstrip(',')
        if not line:
            raise StopIteration
        return json.loads(line)

    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += self.path+')\n'
        return out