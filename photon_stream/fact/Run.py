from .Geometry import Geometry
from .Event import Event
from .JsonLinesGzipReader import JsonLinesGzipReader
from ..PhotonStream import PhotonStream
import datetime as dt


class Run(object):
    def __init__(self, path):
        self.id = None
        self.night = None
        self.reader = JsonLinesGzipReader(path)
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
        event = Event()
        event.geometry = self.geometry

        event.trigger_type = event_dict['TriggerType']
        event.zd = event_dict['ZdPointing']
        event.az = event_dict['AzPointing']
        event.id = event_dict['EventNum']
        event._time_unix_s = event_dict['UnixTimeUTC'][0]
        event._time_unix_us = event_dict['UnixTimeUTC'][1]
        event.run = self
        event.amplitude_saturated_pixels = event_dict['SaturatedPixels']

        ps = PhotonStream()
        ps.slice_duration = 0.5e-9
        ps.time_lines = event_dict['PhotonArrivals']
        event.photon_stream = ps

        event.time = dt.datetime.utcfromtimestamp(
            event._time_unix_s+event._time_unix_us/1e6)
        return event

    def _read_first_event_to_learn_about_run(self):
        first_event_dict = self.reader.__next__()
        self.id = first_event_dict['RUNID']
        self.night = first_event_dict['NIGHT']
        self._first_event = self._event_dict2event(first_event_dict)

    def __repr__(self):
        out = 'Run('
        out += 'Night '+str(self.night)+', '
        out += 'Id '+str(self.id)
        out += ')\n'
        return out