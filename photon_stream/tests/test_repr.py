import numpy as np
import photon_stream as ps
import pkg_resources

run_path = pkg_resources.resource_filename(
    'photon_stream',
    'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz'
)

reader = ps.EventListReader(run_path)
event = reader.__next__()

def test_EventListReader():
    print(reader.__repr__())

def test_Event():
    print(event.__repr__())

def test_photon_stream():
    print(event.photon_stream.__repr__())

def test_ObservationInfo():
    print(event.observation_info.__repr__())

def test_PhotonStreamCluster():
    phs = ps.PhotonStreamCluster(event.photon_stream)
    print(phs.__repr__())

def test_PhotonTimeLineCluster():
    phs = ps.PhotonTimeLineCluster(event.photon_stream.time_lines[0])
    print(phs.__repr__())


sim_path = pkg_resources.resource_filename(
    'photon_stream',
    'tests/resources/cer011014.phs.jsonl.gz'
)

sim_corsika_path = pkg_resources.resource_filename(
    'photon_stream',
    'tests/resources/cer011014'
)

sim_reader = ps.SimulationReader(sim_path, sim_corsika_path)
sim_event = sim_reader.__next__()

def test_SimulationReader():
    print(sim_reader.__repr__())

def test_Event_sim():
    print(sim_event.__repr__())

def test_SimulationTruth():
    print(sim_event.simulation_truth.__repr__())

def test_AirShowerTruth():
    print(sim_event.simulation_truth.air_shower.__repr__())