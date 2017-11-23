import numpy as np
from math import isclose
from .AirShowerTruth import AirShowerTruth


class SimulationTruth(object):
    """
    A FACT simulation truth

    Fields
    ------

    reuse               The unique reuse identifier in a reused CORSIKA event.

    event               The unique event identifier in a CORSIKA run.

    run                 The unique CORSIKA run identifier in FACT simulations.

    air_shower          [optional]
    """

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.run != other.run: return False
            if self.event != other.event: return False
            if self.reuse != other.reuse: return False
            if hasattr(self, 'air_shower'):
                if self.air_shower != other.air_shower: return False
            return True
        else:
            return NotImplemented


    def _info(self):
        out  = 'run '+str(self.run)+', '
        out += 'event '+str(self.event)+', '
        out += 'reuse '+str(self.reuse)
        return out


    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += self._info()
        out += ')\n'
        return out