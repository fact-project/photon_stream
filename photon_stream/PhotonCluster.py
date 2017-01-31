from sklearn.cluster import DBSCAN
import numpy as np

class PhotonStreamCluster(object):
    def __init__(self, photon_stream, eps=0.1, min_samples=20, deg_over_s=0.35e9):

        xyt = photon_stream.flatten()

        if xyt.shape[0] == 0:
            self.labels = np.array([])
            self.number = 0
            return
        fov_radius = photon_stream.geometry['fov_radius']

        xyt[:,0:2] /= (fov_radius*2.0)
        xyt[:,2] /= (fov_radius*2.0)/deg_over_s

        dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(xyt)
        self.labels = dbscan.labels_

        # Number of clusters in labels, ignoring background if present.
        self.number = len(set(self.labels)) - (1 if -1 in self.labels else 0)

    def __repr__(self):
        out = 'PhotonStreamCluster('
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
        out = 'PhotonTimeLineCluster('
        out += 'number of clusters '+str(self.number)
        out += ')\n'
        return out