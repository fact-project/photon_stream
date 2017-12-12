import numpy as np
import photon_stream as ps
from math import isclose

runh = np.array([
     2.11285281e+05,   1.10140000e+04,   1.30702000e+05,
     6.50000000e+00,   1.00000000e+00,   2.20000000e+05,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
    -2.70000005e+00,   2.00000000e+02,   5.00000000e+04,
     1.00000000e+00,   0.00000000e+00,   3.00000012e-01,
     3.00000012e-01,   1.99999996e-02,   1.99999996e-02,
     6.37131520e+08,   6.00000000e+05,   2.00000000e+06,
    -1.33003992e+03,   0.00000000e+00,   4.58059646e-02,
     5.73089600e-01,   5.28304204e-02,   2.50000000e+00,
     2.06999993e+00,   8.19999981e+00,   1.00000001e-01,
     0.00000000e+00,   0.00000000e+00,   1.00002337e+00,
     9.67266317e-03,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   3.77000008e+01,
     1.53287299e-04,   9.38641739e+00,   2.00000009e-03,
     2.99792466e+10,   1.00000000e+00,   5.40302277e-01,
     1.57000005e+00,   1.00000000e-15,   2.09999997e-02,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     2.00000000e+01,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   2.61909604e-01,
     8.99834216e-01,   0.00000000e+00,   1.03899205e+00,
     2.71383405e-01,   1.37035995e+02,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   1.00000001e-01,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   2.50000000e-01,   5.00000000e-01,
     7.50000000e-01,   1.00000000e+00,   5.00000000e-01,
     2.00000003e-01,   9.26406622e-01,   1.12407136e+00,
     1.49600006e+02,   1.49600006e+02,   2.35531822e-01,
     2.06000000e-01,   1.35000005e-01,   2.22000003e-01,
     5.00000000e-01,   0.00000000e+00,   6.34299994e-01,
     6.89499974e-01,   8.73700023e-01,   6.62400007e-01,
     3.89499992e-01,   2.44320607e+00,   9.12400663e-01,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   1.00000000e+00,
     1.00000000e+05,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   3.94600004e-01,
     7.20000029e-01,   9.49599981e-01,  -1.07000005e+00,
     2.06999993e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   6.48199975e-01,
     5.16300023e-01,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   6.77999973e-01,   9.13999975e-01,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,  -1.58060196e+02,
    -3.08136044e+01,   3.45165849e-01,  -4.01833357e-04,
     9.20443854e-04,   1.21066016e+03,   1.20392957e+03,
     1.36447937e+03,   7.97052002e+02,   1.00000000e+00,
     9.94186375e+05,   7.49333188e+05,   6.36143062e+05,
     7.33384188e+05,   1.25051935e+10,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   2.00000000e+02], dtype=np.float32)

evth = np.array([
     2.17433078e+05,   1.00000000e+00,   1.00000000e+00,
     2.78059418e+02,   0.00000000e+00,   0.00000000e+00,
     4.26011350e+06,   8.45676422e+00,   0.00000000e+00,
     2.77926178e+02,   3.09572201e-02,   0.00000000e+00,
     3.00000000e+00,   1.10140010e+07,   0.00000000e+00,
     0.00000000e+00,   1.10140020e+07,   0.00000000e+00,
     0.00000000e+00,   1.10140030e+07,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   1.10140000e+04,   1.30702000e+05,
     6.50000000e+00,   1.00000000e+00,   2.20000000e+05,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
    -2.70000005e+00,   2.00000000e+02,   5.00000000e+04,
     3.00000012e-01,   3.00000012e-01,   1.99999996e-02,
     1.99999996e-02,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     2.00000000e+00,   3.02999992e+01,   2.41000004e+01,
     1.00000000e+00,   0.00000000e+00,   3.00000000e+00,
     3.00000000e+00,   1.13530000e+04,   0.00000000e+00,
     2.00000000e+00,   3.00000000e+00,   1.00000000e+00,
     2.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     1.00000000e+00,   2.70000000e+01,   2.70000000e+01,
     1.50000000e+03,   1.50000000e+03,   1.00000000e+02,
     1.00000000e+02,   1.00000000e+00,  -1.22173049e-01,
     0.00000000e+00,   1.00000000e+00,   2.90000000e+02,
     9.00000000e+02,   1.00000000e+00,   4.24318164e+03,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,  -2.17889551e+04,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   3.00000000e+00,
     3.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   1.00000000e+00,   2.00000000e+04,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   8.00000000e+01,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
     0.00000000e+00,   0.00000000e+00,   0.00000000e+00], dtype=np.float32)


def test_constructor():
    ast = ps.simulation_truth.AirShowerTruth(
        raw_corsika_run_header=runh,
        raw_corsika_event_header=evth
    )

    assert ast.particle == 1.0
    assert isclose(ast.energy, 278.05942, abs_tol=0.001)
