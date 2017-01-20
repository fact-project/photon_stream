from .Event import Event
from .JsonLinesGzipReader import JsonLinesGzipReader


class Run(object):
    def __init__(self, path):
        preview_event = next(JsonLinesGzipReader(path))
        self.id = preview_event['RUNID']
        self.night = preview_event['NIGHT']
        self.reader = JsonLinesGzipReader(path)

    def __iter__(self):
        return self

    def __next__(self):
        return Event.from_event_dict_and_run(
            event_dict=next(self.reader),
            run=self
        )

    def inspect(self):
        return pd.DataFrame([{
            'analog_amplitude_saturations': len(event.amplitude_saturated_pixels),
            'trigger_types': event.trigger_type,
            'total_photon_counts': event.photon_stream.photon_count.sum(),
            'times': event.time,
            'zenith_distances': event.zd,
            'azimuths': event.az,
            'ids': event.id,
            }
            for event in self])


    def __repr__(self):
        out = 'Run('
        out += 'Night '+str(self.night)+', '
        out += 'Id '+str(self.id)
        out += ')\n'
        return out