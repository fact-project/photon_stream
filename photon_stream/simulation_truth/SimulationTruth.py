import numpy as np
from math import isclose


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
        return truth    


    def add_to_dict(self, event_dict):
        ed = event_dict
        ed['Run'] = int(self.run)
        ed['Event'] = int(self.event)
        ed['Reuse'] = int(self.reuse)
        return ed


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            # identification
            if self.run != other.run: return False
            if self.event != other.event: return False
            if self.reuse != other.reuse: return False
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