from sklearn.cluster import DBSCAN
import numpy as np


class PhotonTimeSeriesCluster(object):
    def __init__(self, time_series, eps=10):

        if len(time_series) == 0:
            self.labels = np.array([])
            self.number = 0
            return

        time_series_array = np.array(time_series)
        time_series_array_rs = time_series_array.reshape(-1, 1)

        dbscan = DBSCAN(eps=eps, min_samples=2)
        dbfit = dbscan.fit(time_series_array_rs)

        self.labels = dbfit.labels_
        # Number of clusters in labels, ignoring noise if present.
        self.number = len(set(self.labels)) - (1 if -1 in self.labels else 0)

    def __repr__(self):
        out = 'PhotonTimeSeriesCluster('
        out += 'number of clusters '+str(self.number)
        out += ')\n'
        return out
