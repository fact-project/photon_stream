from .Event import Event
from .EventListReader import EventListReader
from .io import is_gzipped_file
import gzip
from .simulation_truth.corsika_headers import read_corsika_headers_from_file
from .simulation_truth.corsika_headers import IDX_RUNH_RUN_NUMBER
from .simulation_truth.corsika_headers import IDX_EVTH_EVENT_NUMBER
from .simulation_truth.corsika_headers import IDX_EVTH_REUSE_NUMBER
from .simulation_truth.corsika_headers import IDX_EVTH_RUN_NUMBER
from .simulation_truth.AirShowerTruth import AirShowerTruth
import numpy as np


class SimulationReader(object):
    '''
    Reads in both simulated photon-stream events and MMCS CORSIKA run and event
    headers. Returns merged events with full and raw CORSIKA simulation truth.
    '''
    def __init__(self, photon_stream_path, mmcs_corsika_path):
        self.reader = EventListReader(photon_stream_path)
        self.mmcs_corsika_path = mmcs_corsika_path
        self._read_mmcs_corsika_headers()
        self.id_to_index = {}
        for idx in range(self.event_headers.shape[0]):
            event_id = self.event_headers[idx][IDX_EVTH_EVENT_NUMBER]
            #reuse_id = self.event_headers[idx][IDX_EVTH_REUSE_NUMBER]
            self.id_to_index[event_id] = idx
        self.event_passed_trigger = np.zeros(self.event_headers.shape[0], dtype=np.bool8)


    def __iter__(self):
        return self

    def __next__(self):
        event = next(self.reader)
        assert event.simulation_truth.run == self.run_header[IDX_RUNH_RUN_NUMBER]
        idx = self.id_to_index[event.simulation_truth.event]

        assert event.simulation_truth.run == self.event_headers[idx][IDX_EVTH_RUN_NUMBER]
        assert event.simulation_truth.event == self.event_headers[idx][IDX_EVTH_EVENT_NUMBER]
        assert event.simulation_truth.reuse <= self.event_headers[idx][IDX_EVTH_REUSE_NUMBER]
        self.event_passed_trigger[idx] = True

        event.simulation_truth.air_shower =  AirShowerTruth(
            raw_corsika_run_header=self.run_header,
            raw_corsika_event_header=self.event_headers[idx]
        )

        return event


    def _read_mmcs_corsika_headers(self):
        if is_gzipped_file(self.mmcs_corsika_path):
            with gzip.open(self.mmcs_corsika_path, 'rb') as fin:
                headers = read_corsika_headers_from_file(fin)
        else:
            with open(self.mmcs_corsika_path, 'rb') as fin:
                headers = read_corsika_headers_from_file(fin)
        self.run_header = headers['run_header']
        self.event_headers = headers['event_headers']


    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += "photon-stream '" + self.reader.path + "', "
        out += "CORSIKA '" + self.mmcs_corsika_path + "'"
        out += ')\n'
        return out
