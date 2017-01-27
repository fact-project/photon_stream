from .Geometry import Geometry
from .Event import Event
from .JsonLinesGzipReader import JsonLinesGzipReader


class Run(object):
    def __init__(self, path):
        self.reader = JsonLinesGzipReader(path)
        self.geometry = Geometry()

        preview_event = next(JsonLinesGzipReader(path))
        self.id = preview_event['Run']
        self.night = preview_event['Night']

    def __iter__(self):
        return self

    def __next__(self):
        return Event.from_event_dict_and_run(
            event_dict=next(self.reader),
            run=self
        )

    def __repr__(self):
        out = 'Run('
        out += 'Night '+str(self.night)+', '
        out += 'Id '+str(self.id)
        out += ')\n'
        return out