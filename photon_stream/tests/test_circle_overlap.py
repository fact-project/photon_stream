import numpy as np
import photon_stream as ps


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


def test_trigger_warning():
    overlapp = ps.muons.tools.circle_overlapp(
        cx1=0.0, cy1=0.0, r1=1,
        cx2=0.0, cy2=2, r2=2)
