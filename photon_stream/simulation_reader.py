from .event import Event
from .event_list_reader import EventListReader
from .io import is_gzipped_file
import gzip
import os
from .simulation_truth.corsika_headers import read_corsika_headers_from_file
from .simulation_truth.corsika_headers import IDX_RUNH_RUN_NUMBER
from .simulation_truth.corsika_headers import IDX_EVTH_EVENT_NUMBER
from .simulation_truth.corsika_headers import IDX_EVTH_REUSE_NUMBER
from .simulation_truth.corsika_headers import IDX_EVTH_RUN_NUMBER
from .simulation_truth.air_shower_truth import AirShowerTruth
import numpy as np


class SimulationReader(object):
    '''
    Reads in both simulated photon-stream events and MMCS CORSIKA run and event
    headers. Returns merged events with full and raw CORSIKA simulation truth.
    '''
    def __init__(self, photon_stream_path, mmcs_corsika_path=None):
        self._phs_reader = EventListReader(photon_stream_path)
        if mmcs_corsika_path is None:
            self._mmcs_corsika_path = self._guess_corresponding_mmcs_corsika_path(photon_stream_path)
        else:
            self._mmcs_corsika_path = mmcs_corsika_path
        self._read_mmcs_corsika_headers()
        self._event_to_idx = {}
        for idx in range(self.event_headers.shape[0]):
            event_id = self.event_headers[idx][IDX_EVTH_EVENT_NUMBER]
            self._event_to_idx[event_id] = idx

    def __iter__(self):
        return self

    def __next__(self):
        event = next(self._phs_reader)
        assert event.simulation_truth.run == self.run_header[IDX_RUNH_RUN_NUMBER]
        idx = self._event_to_idx[event.simulation_truth.event]
        total_reuses = int(self.event_headers[idx][IDX_EVTH_REUSE_NUMBER])

        assert event.simulation_truth.run == self.event_headers[idx][IDX_EVTH_RUN_NUMBER]
        assert event.simulation_truth.event == self.event_headers[idx][IDX_EVTH_EVENT_NUMBER]
        assert event.simulation_truth.reuse <= total_reuses

        event.simulation_truth.air_shower =  AirShowerTruth(
            raw_corsika_run_header=self.run_header,
            raw_corsika_event_header=self.event_headers[idx]
        )

        return event


    def _read_mmcs_corsika_headers(self):
        if is_gzipped_file(self._mmcs_corsika_path):
            with gzip.open(self._mmcs_corsika_path, 'rb') as fin:
                headers = read_corsika_headers_from_file(fin)
        else:
            with open(self._mmcs_corsika_path, 'rb') as fin:
                headers = read_corsika_headers_from_file(fin)
        self.run_header = headers['run_header']
        self.event_headers = headers['event_headers']


    def _guess_corresponding_mmcs_corsika_path(self, photon_stream_path):
        run_number = int(os.path.basename(photon_stream_path).split('.')[0])
        dirname = os.path.dirname(photon_stream_path)
        ch_path = os.path.join(dirname, '{run:06d}.ch'.format(run=run_number))
        if os.path.exists(ch_path):
            return ch_path
        else:
            return ch_path+'.gz'


    def thrown_events(self):
        _thrown_events = []
        for evtidx in range(self.event_headers.shape[0]):
            for reuseidx in range(int(self.event_headers[evtidx][IDX_EVTH_REUSE_NUMBER])):
                evt = {
                    'run': self.event_headers[evtidx][IDX_EVTH_RUN_NUMBER],
                    'event': self.event_headers[evtidx][IDX_EVTH_EVENT_NUMBER],
                    'reuse': reuseidx,
                    'particle': self.event_headers[evtidx][3-1],
                    'energy': self.event_headers[evtidx][4-1],
                    'theta': self.event_headers[evtidx][11-1],
                    'phi': self.event_headers[evtidx][12-1],
                    'impact_x': self.event_headers[evtidx][98+int(1+reuseidx)-1]/1e2,
                    'impact_y': self.event_headers[evtidx][118+int(1+reuseidx)-1]/1e2,
                    'starting_altitude': self.event_headers[evtidx][5-1]/1e2,
                    'hight_of_first_interaction': self.event_headers[evtidx][7-1]/1e2,
                }
                _thrown_events.append(evt)
        return _thrown_events


    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += "photon-stream '" + self._phs_reader.path + "', "
        out += "CORSIKA '" + self._mmcs_corsika_path + "'"
        out += ')\n'
        return out
