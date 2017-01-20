from photon_stream import Geometry
import numpy as np
from math import nan
from copy import deepcopy

geo = Geometry()

class PhotonStream(object):
    def __init__(self, time_lines=None, slice_duration=0.):
        self.slice_duration = slice_duration
        if time_lines is None:
            self.time_lines = []
        else:
            self.time_lines = time_lines


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

    def __repr__(self):
        info = 'PhotonStream('
        info += str(len(self.time_lines)) + ' time lines, '
        info += str(self.number_photons) + ' photons'
        info += ')'
        return info
