from sklearn.cluster import DBSCAN
import numpy as np


def normalized_photon_stream_cloud_repr(photon_stream, rad_over_s):
    xyt = photon_stream.flatten()
    if xyt.shape[0] == 0:
        return xyt
    fov_radius = photon_stream.geometry['fov_radius']
    xyt[:,0:2] /= (fov_radius*2.0)
    xyt[:,2] /= (fov_radius*2.0)/rad_over_s
    return xyt


class PhotonStreamCluster(object):
    def __init__(self, photon_stream, eps=0.1, min_samples=20, deg_over_s=0.35e9):
        rad_over_s = np.deg2rad(deg_over_s)
        self.xyt = normalized_photon_stream_cloud_repr(
            photon_stream=photon_stream,
            rad_over_s=rad_over_s,
        )

        if self.xyt.shape[0] == 0:
            self.labels = np.array([])
            self.number = 0
            return

        dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(self.xyt)
        self.labels = dbscan.labels_

        # Number of clusters in labels, ignoring background if present.
        self.number = len(set(self.labels)) - (1 if -1 in self.labels else 0)

    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += 'number of clusters '+str(self.number)
        out += ')\n'
        return out


class PhotonTimeLineCluster(object):
    def __init__(self, time_series, eps=10):

        if len(time_series) == 0:
            self.labels = np.array([])
            self.number = 0
            return

        time_series_array = np.array(time_series)
        time_series_array_rs = time_series_array.reshape(-1,1)

        dbscan = DBSCAN(eps=eps, min_samples=2)
        dbfit = dbscan.fit(time_series_array_rs)

        self.labels = dbfit.labels_
        # Number of clusters in labels, ignoring background if present.
        self.number = len(set(self.labels)) - (1 if -1 in self.labels else 0)

    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += 'number of clusters '+str(self.number)
        out += ')\n'
        return out