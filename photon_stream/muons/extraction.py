import numpy as np
from ..Run import Run
from .detection import detection
from ..PhotonCluster import PhotonStreamCluster
import gzip
import os
import json

header_dtype = np.dtype([
    ('Night', np.uint32),
    ('Run', np.uint32),
    ('Event', np.uint32),
    ('UnixTime_s', np.uint32),
    ('UnixTime_us', np.uint32),
    ('Zd', np.float32),
    ('Az', np.float32),
    ('ring_center_x', np.float32),
    ('ring_center_y', np.float32),
    ('ring_radius', np.float32),
    ('arrival_time', np.float32),
    ('ring_overlap_with_fov', np.float32),
    ('number_muon_photons', np.float32)])


def extract_muons_from_run(input_run_path, output_run_path, output_run_header_path):
    """
    Detects and extracts muon candidate events from a run. The muon candidate   
    events are exported into a new output run. In addidion a header for the muon
    candidates is exported. 


    Parameter
    ---------
    input_run_path              Path to the input run.

    output_run_path             Path to the output run of muon candidates.

    output_run_header_path      Path to the binary output run header.


    Binary Output Format Run Header
    -------------------------------
    for each muon candidate:

    1)      uint32      Night
    2)      uint32      Run ID
    3)      uint32      Event ID
    4)      uint32      unix time seconds [s]
    5)      uint32      unix time micro seconds modulo full seconds [us]
    6)      float32     Pointing zenith distance [deg]
    7)      float32     Pointing azimuth [deg]
    8)      float32     muon ring center x [deg]
    9)      float32     muon ring center y [deg]
   10)      float32     muon ring radius [deg]
   11)      float32     mean arrival time muon cluster [s]
   12)      float32     muon ring overlapp with field of view (0.0 to 1.0) [1]
   13)      float32     number of photons muon cluster [1]
    """
    run = Run(input_run_path)
    with gzip.open(output_run_path, 'wt') as f_muon_run, open(output_run_header_path, 'wb') as f_muon_run_header:
        for event in run:

            photon_clusters = PhotonStreamCluster(event.photon_stream)
            muon_features = detection(event, photon_clusters)

            if muon_features['is_muon']:

                # EXPORT EVENT in JSON
                event_dict = event.to_dict()
                json.dump(event_dict, f_muon_run)
                f_muon_run.write('\n')

                # EXPORT EVENT header
                all_photons_in_event = event.photon_stream.flatten()
                muon_cluster = all_photons_in_event[photon_clusters.labels>=0]
                mean_arrival_time_muon_cluster = muon_cluster[:,2].mean()

                head1 = np.zeros(5, dtype=np.uint32)
                head1[0] = event.night
                head1[1] = event.run_id
                head1[2] = event.id
                head1[3] = event._time_unix_s
                head1[4] = event._time_unix_us

                head2 = np.zeros(8, dtype=np.float32)
                head2[0] = event.zd
                head2[1] = event.az
                head2[2] = muon_features['muon_ring_cx']
                head2[3] = muon_features['muon_ring_cy']
                head2[4] = muon_features['muon_ring_r']
                head2[5] = mean_arrival_time_muon_cluster
                head2[6] = muon_features['muon_ring_overlapp_with_field_of_view']
                head2[7] = muon_features['number_of_photons']

                f_muon_run_header.write(head1.tobytes())
                f_muon_run_header.write(head2.tobytes())
            else:
                continue

