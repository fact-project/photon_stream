import numpy as np
import photon_stream as ps
import tempfile
import os
import pkg_resources

def test_run_inspection():
    run_path = pkg_resources.resource_filename(
        'photon_stream', 
        'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz')

    run = ps.Run(run_path)
    inspection = run.inspect()
    assert len(inspection) == 100


def test_run_can_open_file_and_inspect_it():

    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz')

    run = ps.Run(run_path)
    inspection_event_26 = run.inspect().loc[26]
    assert inspection_event_26.trigger_type == 4
    assert inspection_event_26.total_number_of_photons == 6379
    assert inspection_event_26.number_of_saturated_pixels == 0


def test_run_can_iterate_over_file():
    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz')

    for event in ps.Run(run_path):
        pass


def test_event_knows_runid_and_nightint():
    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz')

    event = next(ps.Run(run_path))
    assert event.night == 20170119
    assert event.run_id == 229