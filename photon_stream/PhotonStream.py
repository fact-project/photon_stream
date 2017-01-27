import numpy as np

class PhotonStream(object):
    def __init__(self):
        self.slice_duration = 0.0
        self.time_lines = []

    @classmethod
    def from_event_dict(cls, event_dict):
        ps = cls()
        ps.slice_duration = 0.5e-9
        ps.time_lines = event_dict['PhotonArrivals_500ps']
        return ps

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

    def truncate_time_lines(self, start_time, end_time):
        trunc_ps = PhotonStream()
        trunc_ps.slice_duration = self.slice_duration
        trunc_ps.time_lines = truncate_time_lines(
            time_lines=self.time_lines,
            slice_duration=self.slice_duration,
            start_time=start_time,
            end_time=end_time)
        return trunc_ps

    def __repr__(self):
        info = 'PhotonStream('
        info+= str(len(self.time_lines))+' time lines, '
        info+= str(self._number_photons())+' photons'
        info+= ')'
        return info


def truncate_time_lines(time_lines, slice_duration, start_time, end_time):
    trunc_time_lines = []
    for time_line in time_lines:
        trunc_time_line = []
        for arrival_slice in time_line:
            arrival_time = arrival_slice*slice_duration
            if arrival_time >= start_time and arrival_time < end_time:
                trunc_time_line.append(arrival_slice)
        trunc_time_lines.append(trunc_time_line)

    return trunc_time_lines