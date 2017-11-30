import numpy as np
import photon_stream as ps
import tempfile
import os
import pkg_resources
import gzip

run_path = pkg_resources.resource_filename(
    'photon_stream',
    os.path.join('tests', 'resources', '20170119_229_pass4_100events.phs.jsonl.gz')
)


def test_binary_check():
    with tempfile.TemporaryDirectory(prefix='phs') as tmp:
        path = os.path.join(tmp, 'run.phs.gz')
        ps.jsonl2binary(run_path, path)
        with gzip.open(path, 'rb') as fin:
            assert ps.io.binary.is_phs_binary(fin)


def test_binary_io():
    run = ps.EventListReader(run_path)

    with tempfile.TemporaryDirectory(prefix='photon_stream_test_binary') as tmp:

        bin_run_path = os.path.join(tmp, '20151001_011.phs')

        run_ps = []
        with open(bin_run_path, 'wb') as bf:
            for evt in run:
                run_ps.append(evt.photon_stream)
                ps.io.binary.append_photonstream_to_file(evt.photon_stream, bf)
                ps.io.binary.append_saturated_pixels_to_file(evt.photon_stream.saturated_pixels, bf)

        run_ps_back = []
        with open(bin_run_path, 'rb') as bf:
            while True:
                try:
                    phs = ps.io.binary.read_photonstream_from_file(bf)
                    phs.saturated_pixels = ps.io.binary.read_saturated_pixels_from_file(bf)
                    run_ps_back.append(phs)
                except:
                    break

        assert len(run_ps_back) == len(run_ps)

        for run_index in range(len(run_ps_back)):
            phst0 = run_ps[run_index]
            phst1 = run_ps_back[run_index]

            assert np.abs(phst0.slice_duration - phst1.slice_duration) < 1e-15
            assert phst0 == phst1


def test_jsonl2binary():

    run = ps.EventListReader(run_path)
    run_in = []
    run_back = []
    for event in run:
        run_in.append(event)

    with tempfile.TemporaryDirectory(prefix='phs_test_binary') as tmp:

        binary_path = os.path.join(tmp, '20170119_229.phs.bin')

        with gzip.open(binary_path, 'wb') as fout:
            for event in run_in:
                ps.io.binary.append_event_to_file(event, fout)

        with gzip.open(binary_path, 'rb') as fin:
            while True:
                try:
                    run_back.append(ps.io.binary.read_event_from_file(fin))
                except StopIteration:
                    break

    for i in range(len(run_in)):
        evt_in = run_in[i]
        evt_ba = run_back[i]
        assert evt_in == evt_ba


def test_Descriptor_io():

    d1 = ps.io.binary.Descriptor()
    d1.pass_version = 1
    d1.event_type = 0
    d2 = ps.io.binary.Descriptor()
    d1.pass_version = 4
    d1.event_type = 1
    d3 = ps.io.binary.Descriptor()
    d1.pass_version = 4
    d1.event_type = 1
    d4 = ps.io.binary.Descriptor()
    d1.pass_version = 5
    d1.event_type = 1

    out_descs = [d1, d2, d3, d4]

    with tempfile.TemporaryDirectory(prefix='phs_') as tmp:
        binary_path = os.path.join(tmp, 'descs.bin')

        with gzip.open(binary_path, 'wb') as fout:
            for descs in out_descs:
                ps.io.binary.append_Descriptor_to_file(descs, fout)


        in_descss = []
        with gzip.open(binary_path, 'rb') as fin:
            for i in range(len(out_descs)):
                in_descss.append(
                    ps.io.binary.read_Descriptor_from_file(fin)
                )


    for i in range(len(out_descs)):
        out_h = out_descs[i]
        in_h = in_descss[i]
        assert in_h.magic_1 == ps.io.binary.MAGIC_DESCRIPTOR_1
        assert in_h.magic_2 == ps.io.binary.MAGIC_DESCRIPTOR_2
        assert in_h.magic_3 == ps.io.binary.MAGIC_DESCRIPTOR_3
        assert out_h.pass_version == in_h.pass_version
        assert out_h.event_type == in_h.event_type


def test_io_simulation_events():
    photon_stream_path = pkg_resources.resource_filename(
        'photon_stream',
        os.path.join('tests', 'resources', '011014.phs.jsonl.gz')
    )

    run = ps.EventListReader(photon_stream_path)

    run_in = []
    run_back = []
    for event in run:
        run_in.append(event)

    with tempfile.TemporaryDirectory(prefix='phs_sim_io_test') as tmp:
        binary_path = os.path.join(tmp, '011014.phs.gz')

        with gzip.open(binary_path, 'wb') as fout:
            for event in run_in:
                ps.io.binary.append_event_to_file(event, fout)

        with gzip.open(binary_path, 'rb') as fin:
            while True:
                try:
                    run_back.append(ps.io.binary.read_event_from_file(fin))
                except StopIteration:
                    break

    for i in range(len(run_in)):
        evt_in = run_in[i]
        evt_ba = run_back[i]
        assert evt_in == evt_ba
