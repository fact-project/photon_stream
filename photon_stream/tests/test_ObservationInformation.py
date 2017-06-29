import numpy as np
import photon_stream as ps

event_dict_A = {
    'Run': 1337,
    'Event': 42,
    'Night': 20151224,
    'UnixTime_s_us': [1234,5678],
    'Trigger': 4,
}

event_dict_B = {
    'Run': 99,
    'Event': 56,
    'Night': 20170101,
    'UnixTime_s_us': [9876,54321],
    'Trigger': 5,
}


def test_constructor():
    a = np.abs
    obs = ps.ObservationInformation.from_event_dict(event_dict_A)
    assert obs.run == 1337
    assert obs.night == 20151224
    assert obs.event == 42
    assert obs._time_unix_s == 1234
    assert obs._time_unix_us == 5678
    assert obs.trigger_type == 4


def test_equal():
    obs_info_1A = ps.ObservationInformation.from_event_dict(event_dict_A)
    obs_info_1B = ps.ObservationInformation.from_event_dict(event_dict_B)
    
    obs_info_2A = ps.ObservationInformation.from_event_dict(event_dict_A)
    obs_info_2B = ps.ObservationInformation.from_event_dict(event_dict_B)

    assert obs_info_1A == obs_info_1A
    assert obs_info_1A != obs_info_1B
    assert obs_info_1A == obs_info_2A


def test_repr():
    sim_truth = ps.ObservationInformation.from_event_dict(event_dict_A)
    print(sim_truth.__repr__())