import ujson as json
import os
import gzip
from .is_gzipped_file import is_gzipped_file
from ..Event import Event

class JsonLinesReader:
    def __init__(self, fin):
        self.fin = fin

    def __iter__(self):
        return self

    def __next__(self):
        line = self.fin.readline().strip().rstrip(',')
        if not line:
            raise StopIteration
        event_dict = json.loads(line)
        return Event.from_event_dict(event_dict)

    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += ')\n'
        return out