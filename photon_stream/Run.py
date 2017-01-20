from .Geometry import Geometry
from .Event import Event
from .JsonLinesGzipReader import JsonLinesGzipReader


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
            return Event.from_event_dict_and_run(event_dict, self)

    def _read_first_event_to_learn_about_run(self):
        first_event_dict = self.reader.__next__()
        self.id = first_event_dict['RUNID']
        self.night = first_event_dict['NIGHT']
        self._first_event = Event.from_event_dict_and_run(first_event_dict, self)

    def __repr__(self):
        out = 'Run('
        out += 'Night '+str(self.night)+', '
        out += 'Id '+str(self.id)
        out += ')\n'
        return out