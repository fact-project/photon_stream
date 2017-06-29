import numpy as np
import photon_stream as ps

def test_near():
    assert not ps.tests.tools.near(1.0, 0.0)
    assert not ps.tests.tools.near(0.0, 1.0)
    assert ps.tests.tools.near(0.0, 0.0)
    assert ps.tests.tools.near(1.0, 1.0)
    assert ps.tests.tools.near(1.0, 1.000001)
    assert not ps.tests.tools.near(0.0001, 0.0, 1e-9)