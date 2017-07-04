import numpy as np
from math import isclose
from .AirShowerTruth import AirShowerTruth
from .DetectorTruth import DetectorTruth


class SimulationTruth(object):
    """
    A FACT simulation truth

    Fields
    ------

    reuse               The unique reuse identifier in a reused CORSIKA event.

    event               The unique event identifier in a CORSIKA run.

    run                 The unique CORSIKA run identifier in FACT simulations.

    air_shower          [optional]

    detector            [optional]
    """


    @classmethod
    def from_event_dict(cls, event_dict):
        truth = cls()
        # identification
        truth.run = np.uint32(event_dict['Run'])
        truth.event = np.uint32(event_dict['Event'])
        truth.reuse = np.uint32(event_dict['Reuse'])
        if 'DetectorTruth' in event_dict:
            truth.detector = DetectorTruth.from_event_dict(
                event_dict['DetectorTruth']
            )
        return truth    


    def add_to_dict(self, event_dict):
        ed = event_dict
        ed['Run'] = int(self.run)
        ed['Event'] = int(self.event)
        ed['Reuse'] = int(self.reuse)
        if hasattr(self, 'detector'):
            ed['DetectorTruth'] = self.detector.add_to_dict({})
        return ed


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.run != other.run: return False
            if self.event != other.event: return False
            if self.reuse != other.reuse: return False
            if hasattr(self, 'air_shower'):
                if self.air_shower != other.air_shower: return False
            if hasattr(self, 'detector'):
                if self.detector != other.detector: return False
            return True
        else:
            return NotImplemented


    def _info(self):
        out  = 'run '+str(self.run)+', '
        out += 'event '+str(self.event)+', '
        out += 'reuse '+str(self.reuse)
        return out


    def __repr__(self):
        out = 'SimulationTruth('
        out += self._info()
        out += ')\n'
        return out