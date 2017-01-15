import numpy as np
import photon_stream as ps
import tempfile
import os
import pkg_resources

def test_binary_io():

    run_path = pkg_resources.resource_filename(
        'photon_stream', 
        'tests/resources/20151001_011_pass2_100_events.jsonl.gz')

    run = ps.fact.Run(run_path)

    with tempfile.TemporaryDirectory(prefix='photon_stream_test_binary') as tmp:

        bin_run_path = os.path.join(tmp, '20151001_011.spe')
        
        run_ps = []
        with open(bin_run_path, 'wb') as bf:
            for evt in run:
                run_ps.append(evt.photon_stream)
                ps.binary_read_write.io.append_photonstream_to_binary_file(evt.photon_stream, bf)

        run_ps_back = []
        with open(bin_run_path, 'rb') as bf:
            while True:
                try:
                    phs = ps.binary_read_write.io.read_photonstream_from_binary_file(bf)
                    run_ps_back.append(phs)
                except IndexError:
                    break
        
        assert len(run_ps_back) == len(run_ps)

        for run_index in range(len(run_ps_back)):
            phst0 = run_ps[run_index]
            phst1 = run_ps_back[run_index]

            assert phst0.slice_duration == phst1.slice_duration
            assert len(phst0.time_lines) == len(phst1.time_lines)
            print(len(phst1.time_lines))


            for i in range(len(phst0.time_lines)):
                assert len(phst0.time_lines[i]) == len(phst1.time_lines[i])

                for s in range(len(phst0.time_lines[i])):
                    assert phst0.time_lines[i][s] == phst1.time_lines[i][s]