import numpy as np
from math import isclose


class AirShowerTruth(object):
    """
    Simulation truth on the air-shower as particle type and particle energy.
    Based on the inputs for the KIT CORSIKA air-shower simulation. 
    See the KIT CORSKIA documentation:
    https://web.ikp.kit.edu/corsika/usersguide/usersguide.pdf
    """


    @classmethod
    def from_event_dict(cls, event_dict):
        '''
        See https://web.ikp.kit.edu/corsika/usersguide/usersguide.pdf
        '''
        truth = cls()
        truth.particle = np.uint32(event_dict['Particle'])
        truth.energy = np.float32(event_dict['Energy_GeV'])
        truth.phi = np.float32(event_dict['Phi_deg'])
        truth.theta = np.float32(event_dict['Theta_deg'])
        truth.impact_x = np.float32(event_dict['ImpactX_m'])
        truth.impact_y = np.float32(event_dict['ImpactY_m'])
        truth.first_interaction_altitude = np.float32(event_dict['FirstInteractionAltitude_m'])
        return truth    


    def add_to_dict(self, event_dict):
        ed = event_dict
        ed['Particle'] = int(self.particle)
        ed['Energy_GeV'] = float(self.energy)
        ed['Phi_deg'] = float(self.phi)
        ed['Theta_deg'] = float(self.theta)
        ed['ImpactX_m'] = float(self.impact_x)
        ed['ImpactY_m'] = float(self.impact_y)
        ed['FirstInteractionAltitude_m'] = float(self.first_interaction_altitude)
        return ed


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.particle != other.particle: return False
            if not isclose(self.energy, other.energy, abs_tol=0.1): return False

            if not isclose(self.phi, other.phi, abs_tol=1e-3): return False
            if not isclose(self.theta, other.theta, abs_tol=1e-3): return False

            if not isclose(self.impact_x, other.impact_x, abs_tol=1e-2): return False
            if not isclose(self.impact_y, other.impact_y, abs_tol=1e-2): return False

            if not isclose(self.first_interaction_altitude, other.first_interaction_altitude, abs_tol=1.0): 
                return False

            return True
        else:
            return NotImplemented


    def _info(self):
        out  = 'particle '+str(self.particle)+', '
        out += 'energy {:1.2f}'.format(self.energy)+', '
        out += 'phi {:1.2f}'.format(self.phi)+', '
        out += 'theta {:1.2f}'.format(self.theta)
        return out


    def __repr__(self):
        out = 'AirShowerTruth('
        out += self._info()
        out += ')\n'
        return out