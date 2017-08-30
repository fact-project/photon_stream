import numpy as np
import datetime as dt

class ObservationInformation(object):
    """
    A FACT observation

    Fields
    ------

    event               The unique event identifier in an observation run.

    run                 The unique run identifier in an observation night.

    night               The unique observation night identifier, 
                        Integer 'YYYYmmnn'.

    time                The UNIX datetime when the event was recorded by the 
                        FACT event builder. (uncertainty is 30ms)

    trigger_type        The FACT trigger type of the event.
                            4: Physics trigger (self triggered)
                            1: External trigger 1 (gps pedestals) 
                            2: External trigger 2 (gps pedestals) 
                         1024: Pedestal trigger.
                        For a full overview of the FACT trigger types, see the 
                        [Phd of Patrick Vogler, table 4.3.b]
                        (http://e-collection.library.ethz.ch/eserv/eth:48381/eth-48381-02.pdf)

    _time_unix_s        The raw unix time in full seconds from the raw 
                        observation event header.

    _time_unix_us       The additional raw milli seconds from the raw 
                        observation event header.
                        observation time in seconds = (
                            _time_unix_s + _time_unix_us*1e6)
    """


    def set_time_unix(self, time_unix_s, time_unix_us):
        self._time_unix_s = np.uint32(time_unix_s)
        self._time_unix_us = np.uint32(time_unix_us)
        self.time = dt.datetime.utcfromtimestamp(
            self._time_unix_s + self._time_unix_us/1e6
        )


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


    def _info(self):
        out  = 'night '+str(self.night)+', '
        out += 'run '+str(self.run)+', '
        out += 'event '+str(self.event)
        return out


    def __repr__(self):
        out = 'ObservationInformation('
        out += self._info()
        out += ')\n'
        return out