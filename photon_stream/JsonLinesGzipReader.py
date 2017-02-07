import gzip
import json
import os

class JsonLinesGzipReader(object):
    """
    Sequentially reads a gzipped JSON-Lines file line by line and provides 
    dictionaries for each line.
    """
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.file = gzip.open(path, "rt")

    def __exit__(self):
        self.file.close()

    def __iter__(self):
        return self

    def __next__(self):
        line = self.file.readline()
        try:
            if line[-2] == ',':
                line = line[:-2]
        except:
            raise StopIteration
        return json.loads(line)

    def __repr__(self):
        out = 'JsonLinesGzipReader('
        out += self.path+')\n'
        return out