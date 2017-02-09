import numpy as np
import photon_stream as ps
import tempfile
import os
import pkg_resources
import gzip

def test_binary_io():

    run_path = pkg_resources.resource_filename(
        'photon_stream', 
        'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz')

    run = ps.Run(run_path)

    with tempfile.TemporaryDirectory(prefix='photon_stream_test_binary') as tmp:

        bin_run_path = os.path.join(tmp, '20151001_011.phs')
        
        run_ps = []
        with open(bin_run_path, 'wb') as bf:
            for evt in run:
                run_ps.append(evt.photon_stream)
                ps.experimental.io.append_photonstream_to_file(evt.photon_stream, bf)

        run_ps_back = []
        with open(bin_run_path, 'rb') as bf:
            while True:
                try:
                    phs = ps.experimental.io.read_photonstream_from_file(bf)
                    run_ps_back.append(phs)
                except:
                    break
        
        assert len(run_ps_back) == len(run_ps)

        for run_index in range(len(run_ps_back)):
            phst0 = run_ps[run_index]
            phst1 = run_ps_back[run_index]

            assert np.abs(phst0.slice_duration - phst1.slice_duration) < 1e-15
            assert len(phst0.time_lines) == len(phst1.time_lines)


            for i in range(len(phst0.time_lines)):
                assert len(phst0.time_lines[i]) == len(phst1.time_lines[i])

                for s in range(len(phst0.time_lines[i])):
                    assert phst0.time_lines[i][s] == phst1.time_lines[i][s]


def test_jsonl2binary():

    run_path = pkg_resources.resource_filename(
        'photon_stream', 
        'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz')

    run = ps.Run(run_path)
    run_in = []
    run_back = []
    for event in run:
        run_in.append(event)

    with tempfile.TemporaryDirectory(prefix='phs_test_binary') as tmp:

        binary_path = os.path.join(tmp, '20170119_229.phs.bin')

        with gzip.open(binary_path, 'wb') as fout:
            for event in run_in:
                ps.experimental.io.append_event_to_file(event, fout)

        with gzip.open(binary_path, 'rb') as fin:
            while True:
                try:
                    run_back.append(ps.experimental.io.read_event_from_file(fin))
                except StopIteration:
                    break

    for i in range(len(run_in)):
        evt_in = run_in[i]
        evt_ba = run_back[i]

        # Event Header
        assert evt_in.night == evt_ba.night
        assert evt_in.run_id == evt_ba.run_id
        assert evt_in.id == evt_ba.id

        assert evt_in._time_unix_s == evt_ba._time_unix_s
        assert evt_in._time_unix_us == evt_ba._time_unix_us

        assert evt_in.trigger_type == evt_ba.trigger_type

        assert np.abs(evt_in.zd - evt_ba.zd) < 1e-5
        assert np.abs(evt_in.az - evt_ba.az) < 1e-5

        # Saturated Pixels
        assert len(evt_in.saturated_pixels) == len(evt_ba.saturated_pixels)
        for i, saturated_pixel_in in enumerate(evt_in.saturated_pixels):
            assert saturated_pixel_in == evt_ba.saturated_pixels[i]

        # Photon Stream Header
        assert (evt_in.photon_stream.slice_duration - evt_ba.photon_stream.slice_duration) < 1e-9
        assert evt_in.photon_stream.number_photons == evt_ba.photon_stream.number_photons
        assert len(evt_in.photon_stream.time_lines) == len(evt_ba.photon_stream.time_lines)

        for pixel in range(len(evt_in.photon_stream.time_lines)):
            number_of_photons_in_pixel_in = len(evt_in.photon_stream.time_lines[pixel])
            number_of_photons_in_pixel_ba = len(evt_ba.photon_stream.time_lines[pixel])

            assert number_of_photons_in_pixel_in == number_of_photons_in_pixel_ba

            for photon in range(number_of_photons_in_pixel_in):
                assert evt_in.photon_stream.time_lines[pixel][photon] == evt_ba.photon_stream.time_lines[pixel][photon]
