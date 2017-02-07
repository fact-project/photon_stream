from .Event import Event
from .JsonLinesGzipReader import JsonLinesGzipReader
import pandas as pd

class Run(object):
    """
    A Run() contains Events().
    The Events are not random access but sequentially loaded from a file as 
    needed.
    """
    def __init__(self, path):
        """
        Load a FACT observation run from a file.

        Parameters
        ----------
        path        The path to the observation file.
        """
        self.reader = JsonLinesGzipReader(path)

        preview_event = next(JsonLinesGzipReader(path))
        self.id = preview_event['Run']
        self.night = preview_event['Night']

    def __iter__(self):
        return self

    def __next__(self):
        return Event.from_event_dict_and_run(
            event_dict=next(self.reader),
            run=self)

    def inspect(self):
        """
        Returns a pandas DataFrame() containing a summarized statistics of this 
        run.
        """
        inspection = pd.DataFrame([{
            'number_of_saturated_pixels': len(event.saturated_pixels),
            'trigger_type': event.trigger_type,
            'total_number_of_photons': event.photon_stream.number_photons,
            'time': event.time,
            'zd': event.zd,
            'az': event.az,
            'id': event.id,}
            for event in self])
        inspection.set_index('id', inplace=True)
        return inspection

    def __repr__(self):
        out = 'Run('
        out += 'Night '+str(self.night)+', '
        out += 'Run '+str(self.id)
        out += ')\n'
        return out