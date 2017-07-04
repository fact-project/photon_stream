import numpy as np
import photon_stream as ps
import pkg_resources
import tempfile
import os

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


def test_read_and_write_MMCS_CORSIKA_headers():
    headers_in = ps.simulation_truth.corsika_headers.read_corsika_headers(
        path=mmcs_corsika_path
    )

    with tempfile.TemporaryDirectory(prefix='photon_stream_test_corsika') as tmp:
        ps.simulation_truth.corsika_headers.write_corsika_headers(
            headers=headers_in,
            path=os.path.join(tmp,'headers_out')
        )

        headers_back = ps.simulation_truth.corsika_headers.read_corsika_headers(
            path=os.path.join(tmp,'headers_out')
        )

    np.testing.assert_equal(headers_back['run_header'], headers_in['run_header'])
    np.testing.assert_equal(headers_back['event_headers'], headers_in['event_headers'])
    np.testing.assert_equal(headers_back['run_end'], headers_in['run_end'])



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