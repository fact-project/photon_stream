import photon_stream as ps
import pkg_resources
import os


def test_run_can_iterate_over_file():
    run_path = pkg_resources.resource_filename(
        'photon_stream',
        os.path.join(
            'tests',
            'resources',
            '20170119_229_pass4_100events.phs.jsonl.gz'
        )
    )

    for event in ps.EventListReader(run_path):
        pass


def test_event_knows_runid_and_nightint():
    run_path = pkg_resources.resource_filename(
        'photon_stream',
        os.path.join(
            'tests',
            'resources',
            '20170119_229_pass4_100events.phs.jsonl.gz'
        )
    )

    event = next(ps.EventListReader(run_path))
    assert event.observation_info.night == 20170119
    assert event.observation_info.run == 229
