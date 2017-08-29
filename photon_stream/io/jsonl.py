import ujson as json
import os
import gzip
import numpy as np
from array import array
from ..PhotonStream import PhotonStream
from ..Event import Event
from ..ObservationInformation import ObservationInformation
from ..simulation_truth import SimulationTruth
from . import magic_constants as magic


def read_event_from_dict(event_dict):
    event = Event()
    event.zd = np.float32(event_dict['Zd_deg'])
    event.az = np.float32(event_dict['Az_deg'])
    event.photon_stream = read_PhotonStream_from_dict(event_dict)
    if 'UnixTime_s_us' in event_dict:
        event.observation_info = read_ObservationInformation_from_dict(
            event_dict
        )
    if 'Reuse' in event_dict:
        event.simulation_truth = read_SimulationTruth_from_dict(
            event_dict
        )
    return event


def event_to_dict(event):
    evt = {}
    evt['Zd_deg'] = float(event.zd)
    evt['Az_deg'] = float(event.az)
    evt = append_PhotonStream_to_dict(event.photon_stream, evt)
    if hasattr(event, 'observation_info'):
        evt = append_ObservationInformation_to_dict(event.observation_info, evt)
    if hasattr(event, 'simulation_truth'):
        evt = append_SimulationTruth_to_dict(event.simulation_truth, evt)
    return evt


def read_ObservationInformation_from_dict(event_dict):
    obs = ObservationInformation()
    # identification
    obs.run = np.uint32(event_dict['Run'])
    obs.night = np.uint32(event_dict['Night'])
    obs.event = np.uint32(event_dict['Event'])
    obs.set_time_unix(
        time_unix_s=event_dict['UnixTime_s_us'][0],
        time_unix_us=event_dict['UnixTime_s_us'][1]
    )
    obs.trigger_type = np.uint32(event_dict['Trigger'])
    return obs    


def append_ObservationInformation_to_dict(obs, event_dict):
    ed = event_dict
    ed['Night'] = int(obs.night)
    ed['Run'] = int(obs.run)
    ed['Event'] = int(obs.event)
    ed['UnixTime_s_us'] = [
        int(obs._time_unix_s),
        int(obs._time_unix_us),
    ]
    ed['Trigger'] = int(obs.trigger_type)
    return ed


def read_PhotonStream_from_dict(event_dict):
    ps = PhotonStream()
    ps.slice_duration = np.float32(magic.TIME_SLICE_DURATION_S)
    ps.time_lines = []
    for time_line in event_dict['PhotonArrivals_500ps']:
        ps.time_lines.append(array('B', time_line))
    ps.saturated_pixels = np.array(
        event_dict['SaturatedPixels'],
        dtype=np.uint16
    )
    return ps


def append_PhotonStream_to_dict(phs, event_dict):
    time_lines = []
    for time_line in phs.time_lines:
        time_lines.append(time_line.tolist())
    event_dict['PhotonArrivals_500ps'] = time_lines
    event_dict['SaturatedPixels'] = phs.saturated_pixels.tolist()
    return event_dict


def read_SimulationTruth_from_dict(event_dict):
    truth = SimulationTruth()
    truth.run = np.uint32(event_dict['Run'])
    truth.event = np.uint32(event_dict['Event'])
    truth.reuse = np.uint32(event_dict['Reuse'])
    return truth    


def append_SimulationTruth_to_dict(truth, event_dict):
    ed = event_dict
    ed['Run'] = int(truth.run)
    ed['Event'] = int(truth.event)
    ed['Reuse'] = int(truth.reuse)
    return ed


class Reader:
    def __init__(self, fin):
        self.fin = fin

    def __iter__(self):
        return self

    def __next__(self):
        line = self.fin.readline().strip().rstrip(',')
        if not line:
            raise StopIteration
        event_dict = json.loads(line)
        return read_event_from_dict(event_dict)

    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += ')\n'
        return out