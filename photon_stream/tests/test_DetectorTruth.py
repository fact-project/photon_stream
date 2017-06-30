import numpy as np
import photon_stream as ps
from math import isclose

detector_A = {
    'ShowerPhotonEq': [0.0, 0.0, 0.0, 1.2, 1.3, 3.7, 4.2, 99.4, 1e2, 5.0, 0.0],
}

detector_B = {
    'ShowerPhotonEq': [1.0, 2.0, 3.0, 0.4, 0.5, 0.6, 0.7, 0.8, 1e3, 0.0, 1.0],
}

def test_constructor():
    a = np.abs
    det_tru_A = ps.simulation_truth.DetectorTruth.from_event_dict(detector_A)
    assert len(det_tru_A.shower_photons_in_pixels) == 11


def test_equal():
    det_tru_1A = ps.simulation_truth.DetectorTruth.from_event_dict(detector_A)
    det_tru_1B = ps.simulation_truth.DetectorTruth.from_event_dict(detector_B)
    
    det_tru_2A = ps.simulation_truth.DetectorTruth.from_event_dict(detector_A)
    det_tru_2B = ps.simulation_truth.DetectorTruth.from_event_dict(detector_B)

    assert det_tru_1A == det_tru_1A
    assert det_tru_1A != det_tru_1B
    assert det_tru_1A == det_tru_2A

def test_repr():
    sim_truth = ps.simulation_truth.DetectorTruth.from_event_dict(detector_A)
    print(sim_truth.__repr__())

def test_to_dict():
    det_tru_A = ps.simulation_truth.DetectorTruth.from_event_dict(detector_A)

    dict_back = {'Test': True}
    dict_back = det_tru_A.add_to_dict(dict_back)

    for key in detector_A:
        assert key in dict_back
        if isinstance(detector_A[key], list):
            for i in range(len(detector_A[key])):
                assert isclose(detector_A[key][i], dict_back[key][i], abs_tol=0.1)
        else:
            assert False


def test_simulation_truth():
    sim = ps.simulation_truth.DetectorTruth.from_event_dict(detector_A)
    print(sim.__repr__())