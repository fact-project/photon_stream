from .Geometry import Geometry
from .Event import Event
from .JsonLinesGzipReader import JsonLinesGzipReader


class Run(object):
    def __init__(self, path):
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
        event.id = event_dict['EventId']
        event._time_unix_s = event_dict['UnixTimeUTC'][0]
        event._time_unix_us = event_dict['UnixTimeUTC'][1]
        event.run = self
        event.photon_stream = event_dict['PhotonStream']
        return event

    def _read_first_event_to_learn_about_run(self):
        first_event_dict = self.reader.__next__()
        self.id = first_event_dict['RunId']
        self.night = first_event_dict['NightId']
        self._first_event = self._event_dict2event(first_event_dict)

    def __repr__(self):
        out = 'Run('
        out += 'Night '+str(self.night)+', '
        out += 'Id '+str(self.id)
        out += ')\n'
        return out