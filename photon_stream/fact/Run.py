from .Geometry import Geometry
from .Event import Event
from .._input_output import read_photonstream_from_fact_tools_event_dict
import gzip
import json

class Run(object):
    def __init__(self, path=None):
        self.geometry = Geometry()
        self.events = []

        if path is not None:
            self.load_json_gzip(path)

    def load_json_gzip(self, path):
        event_dicts = []
        with gzip.open(path, "rb") as f:
            event_dicts = json.loads(f.read().decode("ascii"))

        for event_dict in event_dicts:
            ps = read_photonstream_from_fact_tools_event_dict(event_dict)
            event = Event()
            event.geometry = self.geometry
            event.photon_stream = ps
            self.events.append(event)          

    def __getitem__(self, index):
        """
        Returns the index-th event of the run.

        Parameters
        ----------
        index       The index of the event to be returned.  
        """
        return self.events[index]

    def __repr__(self):
        out = 'FactRun('
        out += "path '" + self._path + "', "
        out += str(len(self.events)) + ' events)\n'
        return out