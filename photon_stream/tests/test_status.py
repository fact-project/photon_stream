import numpy as np
import photon_stream as ps
import pkg_resources
import tempfile
import gzip
import json
import os


run_path = pkg_resources.resource_filename(
    'photon_stream',
    os.path.join('tests','resources','20170119_229_pass4_100events.phs.jsonl.gz')
)


def test_number_of_events_in_file():
    assert ps.production.status.number_of_events_in_file(run_path) == 100