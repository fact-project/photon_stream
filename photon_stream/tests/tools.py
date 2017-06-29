import numpy as np

def near(f1, f2, MAX_FLOAT_RESIDUAL=1e-5):
    relative = np.abs(f2 - f1)
    return np.abs(relative) < MAX_FLOAT_RESIDUAL