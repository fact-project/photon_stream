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
        event.run_id = np.uint32(event_dict['Run'])
        event.night = np.uint32(event_dict['Night'])
        event.id = np.uint32(event_dict['Event'])

        event._time_unix_s = np.uint32(event_dict['UnixTime_s_us'][0])
        event._time_unix_us = np.uint32(event_dict['UnixTime_s_us'][1])
        event.trigger_type = np.uint32(event_dict['Trigger'])

        event.zd = np.float32(event_dict['Zd_deg'])
        event.az = np.float32(event_dict['Az_deg'])

        event.saturated_pixels = np.array(event_dict['SaturatedPixels'], dtype=np.uint16)
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

        evt['SaturatedPixels'] = self.saturated_pixels.tolist()
        evt = self.photon_stream.add_to_dict(evt)
        return evt

    def __repr__(self):
        out = 'Event('
        out += 'Night '+str(self.night)+', '
        out += 'Run '+str(self.run_id)+', '
        out += 'Event '+str(self.id)+', '
        out += 'photons '+str(self.photon_stream.number_photons)
        out += ')\n'
        return out

    def assert_equal(
        self, 
        other, 
        max_residual_pointing=1e-5, 
        max_residual_slice_duration=1e-9):
        # Event Header
        assert self.night == other.night
        assert self.run_id == other.run_id
        assert self.id == other.id

        assert self._time_unix_s == other._time_unix_s
        assert self._time_unix_us == other._time_unix_us

        assert self.trigger_type == other.trigger_type

        assert np.abs(self.zd - other.zd) < max_residual_pointing
        assert np.abs(self.az - other.az) < max_residual_pointing

        # Saturated Pixels
        assert len(self.saturated_pixels) == len(other.saturated_pixels)
        for i, saturated_pixel_in in enumerate(self.saturated_pixels):
            assert saturated_pixel_in == other.saturated_pixels[i]

        # Photon Stream Header
        assert (
            (   self.photon_stream.slice_duration - 
                other.photon_stream.slice_duration) < 
            max_residual_slice_duration)
        assert (
            self.photon_stream.number_photons == 
            other.photon_stream.number_photons)
        assert (
            len(self.photon_stream.time_lines) == 
            len(other.photon_stream.time_lines))

        for pixel in range(len(self.photon_stream.time_lines)):
            number_of_photons_in_pixel_in = len(
                self.photon_stream.time_lines[pixel])
            number_of_photons_in_pixel_ba = len(
                other.photon_stream.time_lines[pixel])

            assert number_of_photons_in_pixel_in == number_of_photons_in_pixel_ba

            for photon in range(number_of_photons_in_pixel_in):
                assert (
                    self.photon_stream.time_lines[pixel][photon] == 
                    other.photon_stream.time_lines[pixel][photon])
