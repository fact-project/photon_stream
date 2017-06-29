import pytest
import photon_stream as ps
import pkg_resources
import tempfile
import os


def test_event_can_plot_itself():
    import matplotlib
    matplotlib.use('Agg')

    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz')

    event = next(ps.EventListReader(run_path))
    event.plot()


@pytest.mark.slow
@pytest.mark.nottravis
def test_event_can_be_converted_into_a_video():

    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz')

    event = next(ps.EventListReader(run_path))

    with tempfile.NamedTemporaryFile(suffix='.mp4') as fname:
        ps.plot.save_video(event, fname.name, steps=1)

        assert os.path.isfile(fname.name)
        assert os.path.getsize(fname.name) > 0
