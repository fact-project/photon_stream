import datetime as dt
import numpy as np
from .photon_stream import PhotonStream
from .observation_information import ObservationInformation
from .simulation_truth.SimulationTruth import SimulationTruth
from math import isclose


MAX_RESIDUAL_POINTING_DEG = 1e-3


class Event(object):
    """
    A FACT event in photon-stream representation.

    Fields
    ------
    zd                  The telescope pointing zenith distance in deg.

    az                  The telescope pointing azimuth in deg.

    photon_stream       The photon-stream of all photons detected by all pixels
                        in this event.

    simulation_truth    [optional]

    observation_info    [optional]
    """
    def __init__(self):
        pass


    def _info(self):
        out = ''
        if hasattr(self, 'observation_info'):
            out += 'observation, ' + self.observation_info._info()
        if hasattr(self, 'simulation_truth'):
            out += 'simulation, ' + self.simulation_truth._info()
        return out


    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += self._info() + ', '
        out += 'photon-stream ' + self.photon_stream._info()
        out += ')\n'
        return out


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if not isclose(self.zd, other.zd, abs_tol=MAX_RESIDUAL_POINTING_DEG): return False
            if not isclose(self.az, other.az, abs_tol=MAX_RESIDUAL_POINTING_DEG): return False
            if not self.photon_stream == other.photon_stream: return False
            if hasattr(self, 'simulation_truth'):
                if not self.simulation_truth == other.simulation_truth: return False
            if hasattr(self, 'observation_info'):
                if not self.observation_info == other.observation_info: return False
            return True
        else:
            return NotImplemented
