import numpy as np

class PhotonStream(object):
    def __init__(self):
        self.slice_duration = 0.0
        self.time_lines = []

    def _number_photons(self):
        number_photons = 0
        for time_line in self.time_lines:
            number_photons += len(time_line)
        return number_photons

    def _min_max_arrival_slice(self):
        max_slice = 0
        min_slice = np.iinfo(np.uint64).max
        for time_line in self.time_lines:
            if len(time_line) > 0:
                max_slice_on_current_time_line = max(time_line)
                if max_slice_on_current_time_line > max_slice:
                    max_slice = max_slice_on_current_time_line
                min_slice_on_current_time_line = min(time_line)
                if min_slice_on_current_time_line < min_slice:
                    min_slice = min_slice_on_current_time_line

        return min_slice, max_slice      

    def __repr__(self):
        info = 'PhotonStream('
        info+= str(len(self.time_lines))+' time lines, '
        info+= str(self._number_photons())+' photons'
        info+= ')'
        return info