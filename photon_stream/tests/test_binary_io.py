import pytest
import numpy as np
import photon_stream as ps
import tempfile
import os

def test_read_fact_tools_json():
    run = ps.fact.Run('photon_stream/photon_stream/tests/resources/20150123_016_first25_events.json.gz')
    assert len(run.events) == 25


def test_binary_io():
    run = ps.fact.Run('photon_stream/photon_stream/tests/resources/20150123_016_first25_events.json.gz')

    with tempfile.TemporaryDirectory() as tmp:

        bin_run_path = os.path.join(tmp, '20150123_016.bin')
        
        bf = open(bin_run_path, 'wb')
        for evt in run:
            ps.io.append_photonstream_to_binary_file(evt.photon_stream, bf)
        bf.close()

        bf = open(bin_run_path, 'rb')
        run_read_back = []
        while True:
            try:
                evt = ps.io.read_photonstream_from_binary_file(bf)
                run_read_back.append(evt)
            except IndexError:
                break
        bf.close()
        
        assert len(run_read_back) == len(run.events)

        for run_index in range(len(run.events)):
            phst0 = run[run_index].photon_stream
            phst1 = run_read_back[run_index]

            assert phst0.slice_duration == phst1.slice_duration
            assert len(phst0.time_lines) == len(phst1.time_lines)

            for i in range(len(phst0.time_lines)):
                assert phst0.time_lines[i] == phst1.time_lines[i]