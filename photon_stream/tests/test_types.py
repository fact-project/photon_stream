import numpy as np
from array import array
import datetime as dt
import photon_stream as ps
import pkg_resources
import gzip
import tempfile
import os


run_jsonl_path = pkg_resources.resource_filename(
    'photon_stream',
    os.path.join('tests','resources','20170119_229_pass4_100events.phs.jsonl.gz')
)

def type_check(event):
    assert isinstance(event.zd, np.float32)
    assert isinstance(event.az, np.float32)

    assert isinstance(event.photon_stream, ps.PhotonStream)
    assert isinstance(event.photon_stream.slice_duration, np.float32)
    assert isinstance(event.photon_stream.raw, np.ndarray)
    assert event.photon_stream.raw.dtype == np.uint8
    assert isinstance(event.photon_stream.saturated_pixels, np.ndarray)
    assert event.photon_stream.saturated_pixels.dtype == np.uint16

    if hasattr(event, 'observation_info'):
        assert isinstance(event.observation_info.night, np.uint32)
        assert isinstance(event.observation_info.run, np.uint32)
        assert isinstance(event.observation_info.event, np.uint32)

        assert isinstance(event.observation_info._time_unix_s, np.uint32)
        assert isinstance(event.observation_info._time_unix_us, np.uint32)
        assert isinstance(event.observation_info.time, dt.datetime)


    if hasattr(event, 'simulation_truth'):
        assert isinstance(event.simulation_truth.run, np.uint32)
        assert isinstance(event.simulation_truth.event, np.uint32)
        assert isinstance(event.simulation_truth.reuse, np.uint32)

        assert isinstance(event.simulation_truth.particle, np.uint32)
        assert isinstance(event.simulation_truth.energy, np.float32)
        assert isinstance(event.simulation_truth.phi, np.float32)
        assert isinstance(event.simulation_truth.theta, np.float32)
        assert isinstance(event.simulation_truth.impact_x, np.float32)
        assert isinstance(event.simulation_truth.impact_y, np.float32)
        assert isinstance(event.simulation_truth.first_interaction_altitude, np.float32)


def test_types_from_json():
    run = ps.EventListReader(run_jsonl_path)
    for event in run:
        type_check(event)


def test_types_from_binary():
    with tempfile.TemporaryDirectory(prefix='photon_stream_types') as tmp:

        run_bin_path = os.path.join(tmp, 'run.phs.gz')

        ps.jsonl2binary(
            input_path=run_jsonl_path,
            output_path=run_bin_path,
        )

        with gzip.open(run_bin_path, 'rb') as fin:
            run = ps.io.binary.Reader(fin)
            for event in run:
                type_check(event)
