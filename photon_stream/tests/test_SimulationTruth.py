import numpy as np
import photon_stream as ps

event_dict_A = {
    'Run': 1337,
    'Event': 42,
    'Reuse': 13,
}

event_dict_B = {
    'Run': 1447,
    'Event': 41,
    'Reuse': 0,
}

def test_constructor():
    a = np.abs
    sim_truth_A = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_A)
    assert sim_truth_A.run == 1337
    assert sim_truth_A.event == 42
    assert sim_truth_A.reuse == 13

def test_equal():
    sim_truth_1A = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_A)
    sim_truth_1B = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_B)
    
    sim_truth_2A = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_A)
    sim_truth_2B = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_B)

    assert sim_truth_1A == sim_truth_1A
    assert sim_truth_1A != sim_truth_1B
    assert sim_truth_1A == sim_truth_2A

def test_repr():
    sim_truth = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_A)
    print(sim_truth.__repr__())

def test_to_dict():
    sim_truth_A = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_A)

    dict_back = {'Test': True}
    dict_back = sim_truth_A.add_to_dict(dict_back)

    for key in event_dict_A:
        assert key in dict_back
        assert np.abs(dict_back[key] - event_dict_A[key]) < 1e-3


def test_simulation_truth():
    sim = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_A)
    print(sim.__repr__())