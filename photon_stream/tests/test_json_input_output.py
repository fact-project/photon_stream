import numpy as np
import photon_stream as ps
import tempfile
import os
import pkg_resources
import gzip
import json


def test_run_inspection():
    run_path = pkg_resources.resource_filename(
        'photon_stream',
        os.path.join(
            'tests',
            'resources',
            '20170119_229_pass4_100events.phs.jsonl.gz'
        )
    )

    with tempfile.TemporaryDirectory(prefix='photon_stream_test_json') as tmp:
        in_run = ps.EventListReader(run_path)
        output_run_path = os.path.join(tmp, '20170119_229_out.phs.jsonl.gz')
        with gzip.open(output_run_path, 'wt') as fout:
            for event in in_run:
                json.dump(ps.io.jsonl.event_to_dict(event), fout)
                fout.write('\n')

        in_run = ps.EventListReader(run_path)
        in_run_back = ps.EventListReader(output_run_path)

        for in_event in in_run:
            back_event = in_run_back.__next__()
            assert in_event == back_event
