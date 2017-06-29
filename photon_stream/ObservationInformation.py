import numpy as np
import datetime as dt

class ObservationInformation(object):

    @classmethod
    def from_event_dict(cls, event_dict):

        obs = cls()
        # identification
        obs.run = np.uint32(event_dict['Run'])
        obs.night = np.uint32(event_dict['Night'])
        obs.event = np.uint32(event_dict['Event'])

        obs._time_unix_s = np.uint32(event_dict['UnixTime_s_us'][0])
        obs._time_unix_us = np.uint32(event_dict['UnixTime_s_us'][1])
        obs.time = dt.datetime.utcfromtimestamp(
            obs._time_unix_s + obs._time_unix_us / 1e6)

        obs.trigger_type = np.uint32(event_dict['Trigger'])
        return obs    


    def __eq__(self, other):
        
        if isinstance(other, self.__class__):
            # identification
            if self.run != other.run: return False
            if self.night != other.night: return False
            if self.event != other.event: return False
            
            if self._time_unix_s != other._time_unix_s: return False
            if self._time_unix_us != other._time_unix_us: return False
            if self.trigger_type != other.trigger_type: return False

            return True
        else:
            return NotImplemented


    def __repr__(self):
        out = 'ObservationInformation('
        out += 'Run '+str(self.run)+', '
        out += 'Night '+str(self.night)+', '
        out += 'Event '+str(self.event)
        out += ')\n'
        return out