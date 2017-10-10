import fact
import numpy as np


pixels = fact.instrument.get_pixel_dataframe()
pixels.sort_values('CHID', inplace=True)

class Geometry():
    def __init__(self):
        self.x_angle = np.deg2rad(pixels.x_angle.as_matrix())
        self.y_angle = np.deg2rad(pixels.y_angle.as_matrix())
        self.fov_radius = np.deg2rad(fact.instrument.camera.FOV_RADIUS)

GEOMETRY = Geometry()