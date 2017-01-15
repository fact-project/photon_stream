import gzip
import json
import os
from ..PhotonStream import PhotonStream

class JsonLinesGzipReader(object):
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
        event_dict = json.loads(line)
        
        ps = PhotonStream()
        ps.slice_duration = 0.5e-9
        ps.time_lines = event_dict['PhotonStream']
        
        event_dict['PhotonStream'] = ps
        return event_dict

    def __repr__(self):
        out = 'JsonLinesGzipReader('
        out += self.path+')\n'
        return out