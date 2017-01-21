from datetime import datetime
import matplotlib.pyplot as plt
from .PhotonStream import PhotonStream
from .plot import add_event_2_ax


class Event(object):
    def __init__(self):
        self.trigger_type = None
        self.photon_stream = None
        self.id = None
        self._run = None
        self.time = None
        self.amplitude_saturated_pixels = None

    @property
    def night(self):
        return self._run.night

    @property
    def run(self):
        return self._run.id

    @classmethod
    def from_event_dict_and_run(cls, event_dict, run):
        event = cls()

        event.trigger_type = event_dict['TriggerType']
        event.zd = event_dict['ZdPointing']
        event.az = event_dict['AzPointing']
        event.id = event_dict['EventNum']
        event.amplitude_saturated_pixels = event_dict['SaturatedPixels']
        event.time = datetime.utcfromtimestamp(
            event_dict['UnixTimeUTC'][0] + event_dict['UnixTimeUTC'][1] / 1e6
        )

        event._run = run

        event.photon_stream = PhotonStream.from_event_dict(event_dict)
        return event

    def plot(self, mask=None):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        add_event_2_ax(self, ax, mask=mask)
        plt.show()

    def __repr__(self):
        out = 'FactEvent('
        out += 'Id '+str(self.id)
        out += ')\n'
        return out