import numpy as np
import photon_stream as ps
import pkg_resources

mmcs_corsika_path = pkg_resources.resource_filename(
    'photon_stream',
    'tests/resources/cer011014')

def test_read_MMCS_CORSIKA_headers():
    headers = ps.simulation_truth.corsika_headers.read_corsika_headers(
        mmcs_corsika_path
    )
    assert 'run_header' in headers
    assert 'event_headers' in headers
    assert 'run_end' in headers


def test_read_in_full_CORSIKA_simulation_truth():
    photon_stream_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/cer011014.phs.jsonl.gz')

    simread = ps.SimulationReader(
        photon_stream_path=photon_stream_path, 
        mmcs_corsika_path=mmcs_corsika_path
    )

    events = []
    for event in simread:
        events.append(event)

    assert len(events) == simread.event_passed_trigger.sum()