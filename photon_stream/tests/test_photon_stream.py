import photon_stream as ps
import pkg_resources
import os

run_path = pkg_resources.resource_filename(
    'photon_stream',
    os.path.join('tests','resources','20170119_229_pass4_100events.phs.jsonl.gz')
)

def test_properties():
    event = next(ps.EventListReader(run_path))
    assert event.photon_stream.number_photons == 4984
    assert event.photon_stream.point_cloud.shape == (4984, 3)
    assert event.photon_stream.image_sequence.shape == (
        ps.io.magic_constants.NUMBER_OF_TIME_SLICES,
        ps.io.magic_constants.NUMBER_OF_PIXELS
    )
