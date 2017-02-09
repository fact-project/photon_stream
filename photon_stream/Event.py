import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from .PhotonStream import PhotonStream
from .plot import add_event_2_ax

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

        event.trigger_type = event_dict['Trigger']
        event.zd = event_dict['Zd_deg']
        event.az = event_dict['Az_deg']
        event.id = event_dict['Event']
        event._time_unix_s = event_dict['UnixTime_s_us'][0]
        event._time_unix_us = event_dict['UnixTime_s_us'][1]
        event.saturated_pixels = event_dict['SaturatedPixels']
        event.time = dt.datetime.utcfromtimestamp(
            event._time_unix_s + event._time_unix_us / 1e6)

        event.run_id = event_dict['Run']
        event.night = event_dict['Night']

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

    def __repr__(self):
        out = 'Event('
        out += 'Night '+str(self.night)+', '
        out += 'Run '+str(self.run_id)+', '
        out += 'Event '+str(self.id)+', '
        out += 'photons '+str(self.photon_stream.number_photons)
        out += ')\n'
        return out