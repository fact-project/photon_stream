import numpy as np
from ..event_list_reader import EventListReader
from .detection import detection
from ..photon_cluster import PhotonStreamCluster
from ..io.jsonl import event_to_dict
import gzip
import os
import json

rad2deg = np.rad2deg(1)

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

FACT_PHYSICS_SELF_TRIGGER = 4


def extract_muons_from_run(
    input_run_path,
    output_run_path,
    output_run_header_path
):
    """
    Detects and extracts muon candidate events from a run. The muon candidate
    events are exported into a new output run. In addidion a header for the
    muon candidates is exported.


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
    run = EventListReader(input_run_path)
    with gzip.open(output_run_path, 'wt') as f_muon_run, \
        open(output_run_header_path, 'wb') as f_muon_run_header:

        for event in run:

            if (
                event.observation_info.trigger_type ==
                FACT_PHYSICS_SELF_TRIGGER
            ):

                photon_clusters = PhotonStreamCluster(event.photon_stream)
                muon_features = detection(event, photon_clusters)

                if muon_features['is_muon']:

                    # EXPORT EVENT in JSON
                    event_dict = event_to_dict(event)
                    json.dump(event_dict, f_muon_run)
                    f_muon_run.write('\n')

                    # EXPORT EVENT header
                    head1 = np.zeros(5, dtype=np.uint32)
                    head1[0] = event.observation_info.night
                    head1[1] = event.observation_info.run
                    head1[2] = event.observation_info.event
                    head1[3] = event.observation_info._time_unix_s
                    head1[4] = event.observation_info._time_unix_us

                    head2 = np.zeros(8, dtype=np.float32)
                    head2[0] = event.zd
                    head2[1] = event.az
                    head2[2] = muon_features['muon_ring_cx']*rad2deg
                    head2[3] = muon_features['muon_ring_cy']*rad2deg
                    head2[4] = muon_features['muon_ring_r']*rad2deg
                    head2[5] = muon_features['mean_arrival_time_muon_cluster']
                    head2[6] = muon_features[
                        'muon_ring_overlapp_with_field_of_view'
                    ]
                    head2[7] = muon_features['number_of_photons']

                    f_muon_run_header.write(head1.tobytes())
                    f_muon_run_header.write(head2.tobytes())
