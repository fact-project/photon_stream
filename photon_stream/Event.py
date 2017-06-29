import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from .PhotonStream import PhotonStream
from .plot import add_event_2_ax


MAX_RESIDUAL_POINTING_DEG = 1e-5


class Event(object):
    """
    A FACT event in photon-stream representation.

    Fields
    ------
    id                  The unique identifier of the event in its run.

    trigger_type        The FACT trigger type of the event.
                            4: Physics trigger (self triggered)
                            1: External trigger 1 (gps pedestals) 
                            2: External trigger 2 (gps pedestals) 
                         1024: Pedestal trigger.
                        For a full overview of the FACT trigger types, see the 
                        [Phd of Patrick Vogler, table 4.3.b]
                        (http://e-collection.library.ethz.ch/eserv/eth:48381/eth-48381-02.pdf)

    zd                  The telescope pointing zenith distance in deg.

    az                  The telescope pointing azimuth in deg.

    saturated_pixels    A list of pixels in CHID which have time line 
                        saturations out of the DRS4 chips.

    time                The UNIX datetime when the event was recorded by the
                        event builder. (uncertainty is 30ms)

    run_id              The unique run identifier of the run of a night where 
                        this events belongs to.

    night               The unique night identifier indicating the night when 
                        this event was recorded. Integer 'YYYYmmnn'.

    photon_stream       The photon-stream of all photons detected by all pixels
                        in this event.
    """
    def __init__(self):
        pass

    @classmethod
    def from_event_dict_and_run(cls, event_dict):
        """
        Usually called by the Run() to produce Event() using the raw dictionary 
        out of the 'YYYYmmnn_rrr.phs.jsonl.gz' files.
        """
        event = cls()
        event.run_id = np.uint32(event_dict['Run'])
        event.night = np.uint32(event_dict['Night'])
        event.id = np.uint32(event_dict['Event'])

        event._time_unix_s = np.uint32(event_dict['UnixTime_s_us'][0])
        event._time_unix_us = np.uint32(event_dict['UnixTime_s_us'][1])
        event.trigger_type = np.uint32(event_dict['Trigger'])

        event.zd = np.float32(event_dict['Zd_deg'])
        event.az = np.float32(event_dict['Az_deg'])

        event.time = dt.datetime.utcfromtimestamp(
            event._time_unix_s + event._time_unix_us / 1e6)

        event.photon_stream = PhotonStream.from_event_dict(event_dict)
        return event

    def plot(self, mask=None):
        """
        Creates a new figure with 3D axes to show the photon-stream of the 
        event. Call plt.show() to see it. 
        """
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        add_event_2_ax(self, ax, mask=mask)

    def to_dict(self):
        evt = {}
        evt['Run'] = int(self.run_id)
        evt['Night'] = int(self.night)
        evt['Event'] = int(self.id)

        evt['UnixTime_s_us'] = [int(self._time_unix_s), int(self._time_unix_us)]
        evt['Trigger'] = int(self.trigger_type)

        evt['Zd_deg'] = float(self.zd)
        evt['Az_deg'] = float(self.az)

        evt = self.photon_stream.add_to_dict(evt)
        return evt

    def __repr__(self):
        out = 'Event('
        out += 'Night '+str(self.night)+', '
        out += 'Run '+str(self.run_id)+', '
        out += 'Event '+str(self.id)+', '
        out += 'photon-stream ' + self.photon_stream._info()
        out += ')\n'
        return out


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            # identification
            if not self.night == other.night: return False
            if not self.run_id == other.run_id: return False
            if not self.id == other.id: return False

            if not self._time_unix_s == other._time_unix_s: return False
            if not self._time_unix_us == other._time_unix_us: return False

            if not self.trigger_type == other.trigger_type: return False

            if not np.abs(self.zd - other.zd) < MAX_RESIDUAL_POINTING_DEG: return False
            if not np.abs(self.az - other.az) < MAX_RESIDUAL_POINTING_DEG: return False

            # Photon Stream Header
            if not self.photon_stream == other.photon_stream: return False
            return True
        else:
            return NotImplemented