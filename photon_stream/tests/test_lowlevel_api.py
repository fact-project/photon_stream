import numpy as np
import photon_stream as ps
import pkg_resources
import tempfile
import os

def test_run_can_open_file_and_inspect_it():

    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20151001_011_pass3beta_100_events.jsonl.gz')

    run = ps.Run(run_path)
    inspection_event_26 = run.inspect().loc[26]
    assert inspection_event_26.trigger_type == 4
    assert inspection_event_26.total_photon_count == 2303
    assert inspection_event_26.analog_amplitude_saturation == 0

def test_run_can_iterate_over_file():
    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20151001_011_pass3beta_100_events.jsonl.gz')

    for event in ps.Run(run_path):
        pass

def test_event_knows_runid_and_nightint():
    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20151001_011_pass3beta_100_events.jsonl.gz')

    event = next(ps.Run(run_path))
    assert event.night == 20150716
    assert event.run == 87

def test_photonstream_properties():
    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20151001_011_pass3beta_100_events.jsonl.gz')

    event = next(ps.Run(run_path))

    assert event.photon_stream.number_photons == 2429
    assert event.photon_stream.flatten().shape == (2429, 3)

    assert event.photon_stream.min_arrival_slice == 30
    assert event.photon_stream.max_arrival_slice == 129
    assert event.photon_stream.number_of_clusters == 1
    assert (event.photon_stream.labels == 0).sum() == 148

def test_photonstream_can_truncate_itself():
    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20151001_011_pass3beta_100_events.jsonl.gz')

    event = next(ps.Run(run_path))
    event.photon_stream.truncated_time_lines(30e-9, 130e-9)
