from .Geometry import Geometry
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from .plot import add_event_2_ax


class Event(object):
    def __init__(self):
        self.geometry = None
        self.trigger_type = None
        self.photon_stream = None
        self.id = None
        self.run = None
        self._time_unix_s = None
        self._time_unix_us = None
        self.time = None
        self.amplitude_saturated_pixels = None

    def plot(self, mask=None):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        add_event_2_ax(self, ax, mask=mask)
        plt.show()

    def __repr__(self):
        out = 'FactEvent('
        out += 'Id '+str(self.id)
        out += ')\n'
        return out