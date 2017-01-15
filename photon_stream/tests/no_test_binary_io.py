import pytest
import numpy as np
import photon_stream as ps
import tempfile
import os

def test_binary_io():

    test_run_path = pkg_resources.resource_filename(
        'photon_stream', 
        'tests/resources/20151001_011_fact_tools_pass2_100_events.jsonl.gz')

    run = ps.fact.Run(test_run_path)

    with tempfile.TemporaryDirectory(prefix='photon_stream_test_binary') as tmp:

        bin_run_path = os.path.join(tmp, '20151001_011.bin')
        
        with open(bin_run_path, 'wb') as bf:
            for evt in run:
                ps.io.append_photonstream_to_binary_file(evt.photon_stream, bf)

        with open(bin_run_path, 'rb') as bf:
            run_read_back = []
            while True:
                try:
                    evt = ps.io.read_photonstream_from_binary_file(bf)
                    run_read_back.append(evt)
                except IndexError:
                    break
        
        assert len(run_read_back) == len(run.events)

        for run_index in range(len(run.events)):
            phst0 = run[run_index].photon_stream
            phst1 = run_read_back[run_index]

            assert phst0.slice_duration == phst1.slice_duration
            assert len(phst0.time_lines) == len(phst1.time_lines)
            print(len(phst1.time_lines))


            for i in range(len(phst0.time_lines)):
                assert len(phst0.time_lines[i]) == len(phst1.time_lines[i])

                for s in range(len(phst0.time_lines[i])):
                    assert phst0.time_lines[i][s] == phst1.time_lines[i][s]