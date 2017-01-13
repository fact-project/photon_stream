from sklearn.cluster import DBSCAN
import numpy as np

class PhotonCluster(object):
    def __init__(self, event, eps=0.1, min_samples=20, deg_over_s=0.35e9):
        xyt = event.flatten_photon_stream()

        xyt[:,0:2] /= (event.geometry.fov_radius*2.0)
        xyt[:,2] /= (event.geometry.fov_radius*2.0)/deg_over_s

        dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(xyt)
        self.labels = dbscan.labels_

        # Number of clusters in labels, ignoring noise if present.
        self.number = len(set(self.labels)) - (1 if -1 in self.labels else 0)


class PhotonClusterOnTimeSeries(object):
    def __init__(self, time_series, eps=10):

        time_series_array = np.array(time_series)
        time_series_array_rs = time_series_array.reshape(-1,1)

        dbscan = DBSCAN(eps=eps, min_samples=2)
        dbfit = dbscan.fit(time_series_array_rs)

        self.labels = dbfit.labels_
        # Number of clusters in labels, ignoring noise if present.
        self.number = len(set(self.labels)) - (1 if -1 in self.labels else 0)