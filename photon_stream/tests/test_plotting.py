import pytest
import numpy as np
import photon_stream as ps
import pkg_resources
import tempfile
import os

def test_event_can_plot_itself():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20151001_011_pass3beta_100_events.jsonl.gz')

    event = next(ps.Run(run_path))

    fig, ax = plt.subplots(1, 1)
    event.plot()

@pytest.mark.slow
def test_event_can_be_converted_into_a_video():

    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20151001_011_pass3beta_100_events.jsonl.gz')

    event = next(ps.Run(run_path))

    with tempfile.NamedTemporaryFile(suffix='.mp4') as fname:

        ps.save_video(event, fname.name, steps=1)
        assert os.path.isfile(fname.name)

