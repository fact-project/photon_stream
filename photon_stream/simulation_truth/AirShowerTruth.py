import numpy as np
from math import isclose


class AirShowerTruth(object):
    """
    Simulation truth on the air-shower as particle type and particle energy.
    Based on the inputs for the KIT CORSIKA air-shower simulation. 
    See the KIT CORSKIA documentation:
    https://web.ikp.kit.edu/corsika/usersguide/usersguide.pdf
    """

    def __init__(self, raw_corsika_run_header, raw_corsika_event_header):
        self.raw_corsika_run_header = raw_corsika_run_header
        self.raw_corsika_event_header = raw_corsika_event_header


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if len(self.raw_corsika_run_header) != len(other.raw_corsika_run_header): 
                return False
            for i in range(len(self.raw_corsika_run_header)):
                if self.raw_corsika_run_header[i] != other.raw_corsika_run_header[i]:
                    return False
            if len(self.raw_corsika_event_header) != len(other.raw_corsika_event_header): 
                return False
            for i in range(len(self.raw_corsika_event_header)):
                if self.raw_corsika_event_header[i] != other.raw_corsika_event_header[i]:
                    return False
            return True
        else:
            return NotImplemented


    def _info(self):
        out  = 'particle ID {:1.0f}'.format(self.particle)+', '
        out += 'energy {:1.2f}'.format(self.energy)+', '
        out += 'phi {:1.2f}'.format(self.phi)+', '
        out += 'theta {:1.2f}'.format(self.theta)
        return out


    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += self._info()
        out += ')\n'
        return out

    @property
    def particle(self):
        return self.raw_corsika_event_header[3-1]

    @property
    def energy(self):
        return self.raw_corsika_event_header[4-1]

    @property
    def phi(self):
        return self.raw_corsika_event_header[12-1]

    @property
    def theta(self):
        return self.raw_corsika_event_header[11-1]

    @property
    def total_reuse(self):
        return self.raw_corsika_event_header[98-1]

    @property
    def starting_altitude(self):
        return self.raw_corsika_event_header[5-1]

    @property
    def hight_of_first_interaction(self):
        return self.raw_corsika_event_header[7-1]

    def impact_x(self, reuse):
        return self.raw_corsika_event_header[98+int(reuse)-1]

    def impact_y(self, reuse):
        return self.raw_corsika_event_header[118+int(reuse)-1]