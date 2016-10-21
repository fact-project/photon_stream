from .Geometry import Geometry
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from .plot import add_event_2_ax

class Event(object):
    def __init__(self): 
        self.geometry = None
        self.photon_stream = None

    def flatten_photon_stream(self, start_time=15e-9, end_time=55e-9):
        xyt = []
        for px, pixel_photons in enumerate(self.photon_stream.time_lines):
            for photon_slice in pixel_photons:
                    xyt.append(np.array([
                        self.geometry.dir_x[px],
                        self.geometry.dir_y[px],
                        photon_slice*self.photon_stream.slice_duration
                        ]))
        xyt = np.array(xyt) 
        past_start = xyt[:,2] >= start_time
        before_end = xyt[:,2] <= end_time
        return xyt[past_start*before_end]

    def plot(self, mask=None):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        add_event_2_ax(self, ax, mask=mask)
        plt.show()

    def __repr__(self):
        out = 'FactEvent('
        out += ')\n'
        return out
