import ujson as json
import os
import gzip


class JsonLinesReader:
    """
    Sequentially reads a JSON-Lines file line by line and provides
    dictionaries for each line. Also supports gzipped files.
    """
    def __init__(self, path):
        self.path = os.path.abspath(path)

        # check for gzip file
        with open(path, 'rb') as f:
            marker = f.read(2)
            gzipped = marker[0] == 31 and marker[1] == 139

        if gzipped:
            self.file = gzip.open(path, 'rb')
        else:
            self.file = open(path, 'rb')

    def __exit__(self):
        self.file.close()

    def __iter__(self):
        return self

    def __next__(self):
        line = self.file.readline().decode('utf-8').strip().rstrip(',')
        if not line:
            raise StopIteration
        return json.loads(line)

    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += self.path+')\n'
        return out
