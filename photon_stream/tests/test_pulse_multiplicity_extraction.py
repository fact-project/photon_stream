import numpy as np
import photon_stream as ps
import pkg_resources

def test_empty_time_series():

    pixel_time_series = []
    clusters = ps.fact.PhotonTimeSeriesCluster(pixel_time_series)


def test_pulse_multiplicity_extraction_api():

    run_path = pkg_resources.resource_filename(
        'photon_stream', 
        'tests/resources/20151001_011_pass2_100_events.jsonl.gz')

    run = ps.fact.Run(run_path)

    counter = 0
    for event in run:
        counter += 1
        if counter > 10:
            break
        for pixel_time_series in event.photon_stream.time_lines:
            clusters = ps.fact.PhotonTimeSeriesCluster(pixel_time_series)