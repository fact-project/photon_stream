from math import nan
from copy import deepcopy
import fact
import numpy as np
from array import array

pixels = fact.pixels.get_pixel_dataframe()
pixels.sort_values('CHID', inplace=True)

geometry = {
    'pixel_azimuth': pixels.azimuth.as_matrix(),
    'pixel_zenith': pixels.zenith.as_matrix(),
    'fov_radius': fact.pixels.FOV_RADIUS,
}

class PhotonStream(object):
    def __init__(self, time_lines=None, slice_duration=nan):
        self.slice_duration = slice_duration
        self.geometry = geometry
        if time_lines is None:
            self.time_lines = []
        else:
            self.time_lines = time_lines

    @classmethod
    def from_event_dict(cls, event_dict):
        ps = cls()
        ps.slice_duration = np.float32(0.5e-9)
        ps.time_lines = []
        for time_line in event_dict['PhotonArrivals_500ps']:
            ps.time_lines.append(array('B', time_line))
        return ps

    def add_to_dict(self, event_dict):

        time_lines = []
        for time_line in self.time_lines:
            time_lines.append(time_line.tolist())

        event_dict['PhotonArrivals_500ps'] = time_lines
        return event_dict

    @property
    def photon_count(self):
        return np.array(
            [len(tl) for tl in self.time_lines], 
            dtype=np.int64)

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

    def flatten(self):
        xyt = []
        for px, pixel_photons in enumerate(self.time_lines):
            for photon_slice in pixel_photons:
                    xyt.append([
                        geometry['pixel_azimuth'][px],
                        geometry['pixel_zenith'][px],
                        photon_slice * self.slice_duration
                        ])
        return np.array(xyt)

    def __repr__(self):
        info = 'PhotonStream('
        info += str(len(self.time_lines)) + ' time lines, '
        info += str(self.number_photons) + ' photons'
        info += ')'
        return info