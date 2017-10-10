from math import nan
from copy import deepcopy
import fact
import numpy as np

pixels = fact.instrument.get_pixel_dataframe()
pixels.sort_values('CHID', inplace=True)

geometry = {
    'x_angle': np.deg2rad(pixels.x_angle.as_matrix()),
    'y_angle': np.deg2rad(pixels.y_angle.as_matrix()),
    'fov_radius': np.deg2rad(fact.instrument.camera.FOV_RADIUS),
}

MAX_RESIDUAL_SLICE_DURATION_NS = 1e-9

class PhotonStream(object):
    def __init__(self, time_lines=None, slice_duration=nan):
        self.slice_duration = slice_duration
        self.geometry = geometry
        if time_lines is None:
            self.time_lines = []
        else:
            self.time_lines = time_lines


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
        ''' Returns a Nx3 matrix for N photons in the stream. Each row
        represents a photon in the three dimensinal space of x-direction [deg],
        y-direction [deg], and arrival time [s].

        This is an alternative, but equally complete representation of the raw
        photon-stream. It is useful for e.g. directly plotting the photon stream
        into its 3 dimensional space, or for density clustering in the stream.
        '''
        xyt = []
        for px, pixel_photons in enumerate(self.time_lines):
            for photon_slice in pixel_photons:
                    xyt.append([
                        geometry['x_angle'][px],
                        geometry['y_angle'][px],
                        photon_slice * self.slice_duration
                        ])
        return np.array(xyt)


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if not np.abs(self.slice_duration - other.slice_duration) < MAX_RESIDUAL_SLICE_DURATION_NS: return False
            if not self.number_photons == other.number_photons: return False
            if not len(self.time_lines) == len(other.time_lines): return False

            # Saturated Pixels
            if not len(self.saturated_pixels) == len(other.saturated_pixels): return False            
            for i, saturated_pixel_in in enumerate(self.saturated_pixels):
                if not saturated_pixel_in == other.saturated_pixels[i]: return False

            # Raw Photon-Stream
            for pixel in range(len(self.time_lines)):
                number_of_photons_in_pixel_in = len(self.time_lines[pixel])
                number_of_photons_in_pixel_ba = len(other.time_lines[pixel])

                if not number_of_photons_in_pixel_in == number_of_photons_in_pixel_ba:
                    return False

                for photon in range(number_of_photons_in_pixel_in):
                    if not self.time_lines[pixel][photon] == other.time_lines[pixel][photon]:
                        return False

            return True
        else:
            return NotImplemented


    def _info(self):
        info  = str(len(self.time_lines)) + ' time lines, '
        info += str(self.number_photons) + ' photons'
        return info


    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += self._info()
        out += ')'
        return out