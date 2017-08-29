from .Event import Event
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
        out = 'EventListReader('
        out += "path '" + self.path + "'"
        out += ')\n'
        return out



    @staticmethod
    def inspect(path):
        """
        Returns a pandas DataFrame() containing a summarized statistics of this
        run.
        """
        reader = EventListReader(path)
        inspection = pd.DataFrame([{
            'number_of_saturated_pixels': len(event.photon_stream.saturated_pixels),
            'total_number_of_photons': event.photon_stream.number_photons,
            'zd': event.zd,
            'az': event.az,
        } for event in reader])
        """
        'trigger_type': event.trigger_type,
        'time': event.time,
        'id': event.id,
        """
        return inspection
