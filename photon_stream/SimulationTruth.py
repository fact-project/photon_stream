import numpy as np
from .tests.tools import near

class SimulationTruth(object):
    """
    A FACT simulation truth

    Fields
    ------

    reuse               The unique reuse identifier in a reused CORSIKA event.

    event               The unique event identifier in a CORSIKA run.

    run                 The unique CORSIKA run identifier in FACT simulations.

    For more fields see the KIT CORSKIA documentation:
    https://web.ikp.kit.edu/corsika/usersguide/usersguide.pdf
    """


    @classmethod
    def from_event_dict(cls, event_dict):
        '''
        See https://web.ikp.kit.edu/corsika/usersguide/usersguide.pdf
        '''
        truth = cls()
        # identification
        truth.run = np.uint32(event_dict['Run'])
        truth.event = np.uint32(event_dict['Event'])
        truth.reuse = np.uint32(event_dict['Reuse'])

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
        ed['Run'] = int(self.run)
        ed['Event'] = int(self.event)
        ed['Reuse'] = int(self.reuse)

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
            # identification
            if self.run != other.run: return False
            if self.event != other.event: return False
            if self.reuse != other.reuse: return False

            if self.particle != other.particle: return False
            if not near(self.energy, other.energy): return False

            if not near(self.phi, other.phi): return False
            if not near(self.theta, other.theta): return False

            if not near(self.impact_x, other.impact_x): return False
            if not near(self.impact_y, other.impact_y): return False

            if not near(self.first_interaction_altitude, other.first_interaction_altitude): 
                return False

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