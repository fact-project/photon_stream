import numpy as np
import photon_stream as ps
from math import isclose

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
    assert not hasattr(sim_truth_A, 'air_shower')
    assert not hasattr(sim_truth_A, 'detector')

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


def test_hirachy():
    in_C = {
        'Run': 1337,
        'Event': 42,
        'Reuse': 13,
        'AirShowerTruth': {
            'Energy_GeV': 1337.42, 
            'Particle': 1,
            'Phi_deg': 87.9,
            'Theta_deg': 23.6,
            'ImpactX_m': 12.9,
            'ImpactY_m': 42.6,
            'FirstInteractionAltitude_m': 23456.4,
        },
        'DetectorTruth': {'ShowerPhotonEq': [1.0, 0.0, 3.4, 4.2]}
    }

    simC = ps.simulation_truth.SimulationTruth.from_event_dict(in_C)
    assert hasattr(simC, 'air_shower')
    assert hasattr(simC, 'detector')

    simC2 = ps.simulation_truth.SimulationTruth.from_event_dict(in_C)   
    assert simC == simC2
    assert simC.air_shower == simC2.air_shower
    assert simC.detector == simC2.detector

    back_C = {}
    back_C = simC.add_to_dict(back_C)

    assert in_C['Run'] == back_C['Run']
    assert in_C['Event'] == back_C['Event']
    assert in_C['Reuse'] == back_C['Reuse']

    assert isclose(in_C['AirShowerTruth']['Energy_GeV'], back_C['AirShowerTruth']['Energy_GeV'], abs_tol=1e-3)
    assert isclose(in_C['AirShowerTruth']['Particle'], back_C['AirShowerTruth']['Particle'], abs_tol=1e-3)
    assert isclose(in_C['AirShowerTruth']['Phi_deg'], back_C['AirShowerTruth']['Phi_deg'], abs_tol=1e-3)
    assert isclose(in_C['AirShowerTruth']['Theta_deg'], back_C['AirShowerTruth']['Theta_deg'], abs_tol=1e-3)
    assert isclose(in_C['AirShowerTruth']['ImpactX_m'], back_C['AirShowerTruth']['ImpactX_m'], abs_tol=1e-3)
    assert isclose(in_C['AirShowerTruth']['ImpactY_m'], back_C['AirShowerTruth']['ImpactY_m'], abs_tol=1e-3)
    assert isclose(in_C['AirShowerTruth']['FirstInteractionAltitude_m'], back_C['AirShowerTruth']['FirstInteractionAltitude_m'], abs_tol=1e-3)
    
    for i in range(len(in_C['DetectorTruth']['ShowerPhotonEq'])):
        assert isclose(
            in_C['DetectorTruth']['ShowerPhotonEq'][i], 
            back_C['DetectorTruth']['ShowerPhotonEq'][i], 
            abs_tol=1e-3
        )
