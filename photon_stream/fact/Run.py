from .Geometry import Geometry
from .Event import Event
from .._input_output import read_photonstream_from_fact_tools_event_dict
import gzip
import json
import datetime as dt


class JsonGzipReader(object):
    def __init__(self, path):
        self.path = path
        self.event_dicts = self._load_json_gzip(path)
        self._event_iterator = 0

    def _load_json_gzip(self, path):
        with gzip.open(path, "rb") as f:
            return json.loads(f.read().decode("ascii"))

    def __exit__(self):
        self.file.close()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            event_dict = self.event_dicts[self._event_iterator]
            self._event_iterator += 1
        except IndexError:
            raise StopIteration
        return event_dict

    def __repr__(self):
        out = 'FACT.Run.JsonGzipReader('
        out += self.path+')\n'
        return out


class JsonLinesGzipReader(object):
    def __init__(self, path):
        self.path = path
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
        return event_dict

    def __repr__(self):
        out = 'FACT.Run.JsonLinesGzipReader('
        out += self.path+')\n'
        return out


class Run(object):
    def __init__(self, reader):
        self.reader = reader
        self.geometry = Geometry()
        self._event_iterator = 0
        self._read_first_event_to_learn_about_run()

    def __iter__(self):
        return self

    def __next__(self):
        if self._event_iterator == 0:
            self._event_iterator += 1
            return self._first_event
        else:
            event_dict = self.reader.__next__()
            self._event_iterator += 1
            return self._event_dict2event(event_dict)

    def _event_dict2event(self, event_dict):
        ps = read_photonstream_from_fact_tools_event_dict(event_dict)
        event = Event()
        event.geometry = self.geometry
        event.photon_stream = ps
        try:
            event.trigger_type = event_dict['TriggerType']
            event.zd = event_dict['ZdPointing']
            event.az = event_dict['AzPointing']
            event.id = event_dict['EventNum']
            event.time = dt.datetime.utcfromtimestamp(
                event_dict['UnixTimeUTC'][0]+event_dict['UnixTimeUTC'][1]/1e6)
            event.run = self
        except:
            pass
        return event

    def _read_first_event_to_learn_about_run(self):
        first_event_dict = self.reader.__next__()
        self.id = first_event_dict['RUNID']
        self.night = first_event_dict['NIGHT']
        self._first_event = self._event_dict2event(first_event_dict)

    def __repr__(self):
        out = 'FACT.Run('
        out += 'path '+self.reader.path+')\n'
        return out