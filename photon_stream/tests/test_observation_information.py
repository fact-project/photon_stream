import numpy as np
import photon_stream as ps

event_dict_A = {
    'Run': 1337,
    'Event': 42,
    'Night': 20151224,
    'UnixTime_s_us': [1234, 5678],
    'Trigger': 4,
}

event_dict_B = {
    'Run': 99,
    'Event': 56,
    'Night': 20170101,
    'UnixTime_s_us': [9876, 54321],
    'Trigger': 5,
}


def test_constructor():
    a = np.abs
    obs = ps.io.jsonl.read_ObservationInformation_from_dict(event_dict_A)
    assert obs.run == 1337
    assert obs.night == 20151224
    assert obs.event == 42
    assert obs._time_unix_s == 1234
    assert obs._time_unix_us == 5678
    assert obs.trigger_type == 4


def test_equal():
    obs_info_1A = ps.io.jsonl.read_ObservationInformation_from_dict(event_dict_A)
    obs_info_1B = ps.io.jsonl.read_ObservationInformation_from_dict(event_dict_B)

    obs_info_2A = ps.io.jsonl.read_ObservationInformation_from_dict(event_dict_A)
    obs_info_2B = ps.io.jsonl.read_ObservationInformation_from_dict(event_dict_B)

    assert obs_info_1A == obs_info_1A
    assert obs_info_1A != obs_info_1B
    assert obs_info_1A == obs_info_2A


def test_repr():
    sim_truth = ps.io.jsonl.read_ObservationInformation_from_dict(event_dict_A)
    print(sim_truth.__repr__())


def test_to_dict():
    obs_A = ps.io.jsonl.read_ObservationInformation_from_dict(event_dict_A)

    dict_back = {'Test': True}
    dict_back = ps.io.jsonl.append_ObservationInformation_to_dict(obs_A, dict_back)

    for key in event_dict_A:
        assert key in dict_back
        if (isinstance(event_dict_A[key], int) or isinstance(event_dict_A[key], float)):
            assert np.abs(dict_back[key] - event_dict_A[key]) < 1e-3

        elif isinstance(event_dict_A[key], list):
            for i in range(len(event_dict_A[key])):
                assert np.abs(dict_back[key][i] - event_dict_A[key][i]) < 1e-3
        else:
            assert False
