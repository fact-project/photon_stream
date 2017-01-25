import gzip
import json
import os
from math import nan
from copy import deepcopy
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN


from .plot import add_event_2_ax
import fact

__all__ = ['JsonLinesGzipReader', 'PhotonStream', 'Run', 'Event']

pixels = fact.pixels.get_pixel_dataframe()
pixels.sort_values('CHID', inplace=True)


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
                        pixels.azimuth.iloc[px],
                        pixels.zenith.iloc[px],
                        photon_slice * self.slice_duration
                        ])
        xyt = np.array(xyt)
        past_start = xyt[:, 2] >= start_time
        before_end = xyt[:, 2] <= end_time
        return xyt[past_start*before_end]

    @property
    def labels(self):
        if not hasattr(self, '_labels'):
            self._cluster()
        return self._labels

    @property
    def number_of_clusters(self):
        if not hasattr(self, '_number_of_clusters'):
            self._cluster()
        return self._number_of_clusters

    def _cluster(self, eps=0.1, min_samples=20, deg_over_s=0.35e9):
        xyt = self.flatten()

        if xyt.shape[0] == 0:
            self._labels = np.array([])
            self._number_of_clusters = 0
            return

        xyt[:, 0:2] /= (fact.pixels.FOV_RADIUS * 2.0)
        xyt[:, 2] /= (fact.pixels.FOV_RADIUS**2.0) / deg_over_s

        dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(xyt)
        self._labels = dbscan.labels_

        # Number of clusters in labels, ignoring noise if present.
        self._number_of_clusters = (
            len(set(self.labels)) - (1 if -1 in self.labels else 0)
        )

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
        inspection = pd.DataFrame([{
            'analog_amplitude_saturation': len(event.amplitude_saturated_pixels),
            'trigger_type': event.trigger_type,
            'total_photon_count': event.photon_stream.photon_count.sum(),
            'time': event.time,
            'zenith_distance': event.zd,
            'azimuth': event.az,
            'id': event.id,
            }
            for event in self])
        inspection.set_index('id', inplace=True)
        return inspection


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
