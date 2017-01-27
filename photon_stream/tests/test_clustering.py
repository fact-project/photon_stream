import numpy as np
import photon_stream as ps
import pkg_resources


def test_cluster_api():

    run_path = pkg_resources.resource_filename(
        'photon_stream',
        'tests/resources/20151001_011_pass3beta_100_events.jsonl.gz')

    run = ps.Run(run_path)

    cluster_sizes = np.array([1, 3, 1, 0, 0, 1, 1, 1, 0, 2, 1, 2])

    for test_size in cluster_sizes:
        event = next(run)
        assert test_size == event.photon_stream.number_of_clusters
