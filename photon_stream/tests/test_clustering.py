import numpy as np
import photon_stream as ps
import pkg_resources


def test_cluster_api():

    run_path = pkg_resources.resource_filename(
        'photon_stream', 
        'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz')

    run = ps.Run(run_path)

    counter = 0
    for event in run:
        counter += 1
        if counter > 10:
            break
        clusters = ps.PhotonStreamCluster(event)