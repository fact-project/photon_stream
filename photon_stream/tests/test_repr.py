import numpy as np
import photon_stream as ps
import pkg_resources

def test_photon_stream():
    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz')

    reader = ps.ObservationReader(run_path)
    print(reader.__repr__())
    event = reader.__next__()
    print(event.__repr__())

    print(event.photon_stream.__repr__())