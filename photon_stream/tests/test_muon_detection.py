import pytest
import numpy as np
import photon_stream as ps
import tempfile
import os
import pkg_resources


def test_ring_overlapp():
    overlapp = ps.muons.tools.circle_overlapp(
        cx1=0.0, cy1=0.0, r1=1.0,
        cx2=0.0, cy2=2.0, r2=1.0)
    assert overlapp == 0.0

    overlapp = ps.muons.tools.circle_overlapp(
        cx1=0.0, cy1=0.0, r1=2.0,
        cx2=0.0, cy2=0.0, r2=1.0)
    assert overlapp == 1.0

    overlapp = ps.muons.tools.circle_overlapp(
        cx1=0.0, cy1=0.0, r1=100.0,
        cx2=0.0, cy2=100.0, r2=1.0)
    assert np.abs(overlapp - 0.5) < 2e-3

    overlapp = ps.muons.tools.circle_overlapp(
        cx1=0.0, cy1=0.0, r1=100.0,
        cx2=0.0, cy2=99.0, r2=1.0)
    assert overlapp == 1.0

    overlapp = ps.muons.tools.circle_overlapp(
        cx1=0.0, cy1=0.0, r1=100.0,
        cx2=0.0, cy2=101.0, r2=1.0)
    assert overlapp == 0.0


@pytest.mark.slow
def test_muon_detection():

    np.random.seed(seed=1)

    muon_truth_path = pkg_resources.resource_filename(
        'photon_stream',
        os.path.join('tests', 'resources', 'muon_sample_20140101_104.csv')
    )
    muon_truth = np.genfromtxt(muon_truth_path)

    muon_sample_path = pkg_resources.resource_filename(
        'photon_stream',
        os.path.join(
            'tests',
            'resources',
            '20140101_104_muon_sample.phs.jsonl.gz'
        )
    )

    run = ps.EventListReader(muon_sample_path)

    true_positives = 0
    true_negatives = 0

    false_positives = 0
    false_negatives = 0

    for event in run:
        clusters = ps.PhotonStreamCluster(event.photon_stream)
        ret = ps.muons.detection(event, clusters)

        if ret['is_muon']:
            if event.observation_info.event in muon_truth:
                true_positives += 1
            else:
                false_positives += 1
        else:
            if event.observation_info.event in muon_truth:
                false_negatives += 1
            else:
                true_negatives += 1

    precision = true_positives / (true_positives + false_positives)
    sensitivity = true_positives / (true_positives + false_negatives)

    print('precision', precision)
    print('sensitivity', sensitivity)

    assert precision > 0.995
    assert sensitivity > 0.76
