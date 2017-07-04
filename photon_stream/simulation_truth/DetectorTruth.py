import numpy as np
from math import isclose


class DetectorTruth(object):
    '''
    Simulation Truth of the FACT detector as e.g. number of air-shower photons 
    in a pixel, or single pulse origins.
    '''
    @classmethod
    def from_event_dict(cls, event_dict):
        truth = cls()
        truth.shower_photons_in_pixels = np.array(
            event_dict['ShowerPhotonEq'], 
            dtype=np.float32
        )
        return truth    


    def add_to_dict(self, event_dict):
        ed = event_dict
        ed['ShowerPhotonEq'] = self.shower_photons_in_pixels.tolist()
        return ed


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if not len(self.shower_photons_in_pixels) == len(other.shower_photons_in_pixels): return False
            for i in range(len(self.shower_photons_in_pixels)):
                if not isclose(self.shower_photons_in_pixels[i], other.shower_photons_in_pixels[i], abs_tol=0.1):
                    return False
            return True
        else:
            return NotImplemented


    def _info(self):
        out  = 'cherenkov photons {:1.2f}'.format(self.shower_photons_in_pixels.sum())
        return out


    def __repr__(self):
        out = 'DetectorTruth('
        out += self._info()
        out += ')\n'
        return out