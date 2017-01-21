import gzip
import json
import os
from math import nan
from copy import deepcopy
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .plot import add_event_2_ax
from photon_stream import Geometry

geo = Geometry()

__all__ = ['JsonLinesGzipReader', 'PhotonStream', 'Run', 'Event']

class PhotonStream(object):
    def __init__(self, time_lines=None, slice_duration=0.):
        self.slice_duration = slice_duration
        if time_lines is None:
            self.time_lines = []
        else:
            self.time_lines = time_lines

    @classmethod
    def from_event_dict(cls, event_dict):
        ps = cls()
        ps.slice_duration = 0.5e-9
        ps.time_lines = event_dict['PhotonArrivals']
        return ps

    @property
    def photon_count(self):
        return np.array([len(tl) for tl in self.time_lines], dtype=np.int16)

    @property
    def number_photons(self):
        return self.photon_count.sum()

    @property
    def min_arrival_slice(self):
        if self.number_photons > 0:
            return min(min(tl) for tl in self.time_lines if tl)
        else:
            return nan

    @property
    def max_arrival_slice(self):
        if self.number_photons > 0:
            return max(max(tl) for tl in self.time_lines if tl)
        else:
            return nan

    def flatten(self, start_time=15e-9, end_time=65e-9):
        xyt = []
        for px, pixel_photons in enumerate(self.time_lines):
            for photon_slice in pixel_photons:
                    xyt.append([
                        geo.pixel_azimuth[px],
                        geo.pixel_zenith[px],
                        photon_slice * self.slice_duration
                        ])
        xyt = np.array(xyt)
        past_start = xyt[:, 2] >= start_time
        before_end = xyt[:, 2] <= end_time
        return xyt[past_start*before_end]

    def truncated_time_lines(self, start_time, end_time):
        ''' return new PhotonStream with truncated time_lines

        containing only arrival slices contained
        in (start_time, end_time]
        '''
        tmp = PhotonStream(
            time_lines=deepcopy(self.time_lines),
            slice_duration=self.slice_duration
        )
        tmp._truncate_time_lines(start_time, end_time)
        return tmp

    def _truncate_time_lines(self, start_time, end_time):
        ''' truncate self.time_lines

        to contain only arrival slices within (start_time, end_time]
        '''
        for time_line in self.time_lines:
            for arrival_slice in time_line[:]:
                arrival_time = arrival_slice * self.slice_duration
                if arrival_time < start_time:
                    time_line.remove(arrival_slice)
                if arrival_time >= end_time:
                    time_line.remove(arrival_slice)

    def __repr__(self):
        info = 'PhotonStream('
        info += str(len(self.time_lines)) + ' time lines, '
        info += str(self.number_photons) + ' photons'
        info += ')'
        return info


class JsonLinesGzipReader(object):
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.file = gzip.open(path, "rt")

    def __exit__(self):
        self.file.close()

    def __iter__(self):
        return self

    def __next__(self):
        line = self.file.readline()
        try:
            if line[-2] == ',':
                line = line[:-2]
        except:
            raise StopIteration
        return json.loads(line)

    def __repr__(self):
        out = 'JsonLinesGzipReader('
        out += self.path+')\n'
        return out


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
