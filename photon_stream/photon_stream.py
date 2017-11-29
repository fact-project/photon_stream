import numpy as np
from .io import magic_constants
from .representations import raw_phs_to_point_cloud
from .representations import raw_phs_to_list_of_lists
from .representations import raw_phs_to_image_sequence
from .geometry import GEOMETRY

MAX_RESIDUAL_SLICE_DURATION_NS = 1e-9

class PhotonStream(object):
    def __init__(self):
        self.slice_duration = magic_constants.TIME_SLICE_DURATION_S
        self.geometry = GEOMETRY
        self.raw = None

    @property
    def number_photons(self):
        return len(self.raw) - magic_constants.NUMBER_OF_PIXELS

    @property
    def point_cloud(self):
        ''' Returns a Nx3 matrix for N photons in the stream. Each row
        represents a photon in the three dimensinal space of x-direction [rad],
        y-direction [rad], and arrival time [s].

        This is an alternative, but equally complete representation of the raw
        photon-stream. It is useful for e.g. directly plotting the photon stream
        into its 3 dimensional space, or for density clustering in the stream.
        '''
        return raw_phs_to_point_cloud(
            self.raw,
            cx=self.geometry.x_angle,
            cy=self.geometry.y_angle,
        )

    @property
    def list_of_lists(self):
        '''
        Returns a list along all pixels of lists for each photon arrival time slice.
        '''
        return raw_phs_to_list_of_lists(self.raw)


    @property
    def image_sequence(self):
        return raw_phs_to_image_sequence(self.raw)


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if not np.abs(self.slice_duration - other.slice_duration) < MAX_RESIDUAL_SLICE_DURATION_NS: return False

            # Saturated Pixels
            if not len(self.saturated_pixels) == len(other.saturated_pixels): return False
            for i, saturated_pixel_in in enumerate(self.saturated_pixels):
                if not saturated_pixel_in == other.saturated_pixels[i]: return False

            # Raw Photon-Stream
            if not self.raw.shape[0] == other.raw.shape[0]:
                return False

            if not np.all(self.raw == other.raw):
                return False

            return True
        else:
            return NotImplemented


    def _info(self):
        info = str(self.number_photons) + ' photons'
        return info


    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += self._info()
        out += ')'
        return out
