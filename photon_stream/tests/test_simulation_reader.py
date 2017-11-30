import numpy as np
import photon_stream as ps
import pkg_resources
import tempfile
import os

mmcs_corsika_path = pkg_resources.resource_filename(
    'photon_stream',
    os.path.join('tests', 'resources', '011014.ch')
)

photon_stream_path = pkg_resources.resource_filename(
    'photon_stream',
    os.path.join('tests', 'resources', '011014.phs.jsonl.gz')
)

def test_read_MMCS_CORSIKA_headers():
    with open(mmcs_corsika_path, 'rb') as fin:
        headers = ps.simulation_truth.corsika_headers.read_corsika_headers_from_file(fin)
    assert 'run_header' in headers
    assert 'event_headers' in headers
    assert 'run_end' in headers


def test_read_and_write_MMCS_CORSIKA_headers():
    with open(mmcs_corsika_path, 'rb') as fin:
        headers_in = ps.simulation_truth.corsika_headers.read_corsika_headers_from_file(fin)

    with tempfile.TemporaryDirectory(prefix='photon_stream_test_corsika') as tmp:
        with open(os.path.join(tmp, 'headers_out'), 'wb') as fout:
            ps.simulation_truth.corsika_headers.append_corsika_headers_to_file(
                headers=headers_in,
                fout=fout
            )

        with open(os.path.join(tmp, 'headers_out'), 'rb') as fin:
            headers_back = ps.simulation_truth.corsika_headers.read_corsika_headers_from_file(fin)

    np.testing.assert_equal(headers_back['run_header'], headers_in['run_header'])
    np.testing.assert_equal(headers_back['event_headers'], headers_in['event_headers'])
    np.testing.assert_equal(headers_back['run_end'], headers_in['run_end'])



def test_read_in_full_CORSIKA_simulation_truth():
    simread = ps.SimulationReader(
        photon_stream_path=photon_stream_path,
        mmcs_corsika_path=mmcs_corsika_path
    )

    events = []
    for event in simread:
        events.append(event)


def test_guess_corsika_header_path():
    simread = ps.SimulationReader(
        photon_stream_path=photon_stream_path
    )

    events = []
    for event in simread:
        events.append(event)
