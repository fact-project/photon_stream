import numpy as np
from .PhotonCluster import PhotonTimeSeriesCluster
import tqdm
import json

def finger_histogram(time_series, max_multiplicity=20):
    counts = np.zeros(max_multiplicity, dtype=np.int64)

    if len(time_series) < 1:
        return counts

    clusters = PhotonTimeSeriesCluster(time_series)
    # single photons
    counts[0] = (clusters.labels == -1).sum()

    for label in range(clusters.number):
        number_of_photons_in_cluster = (clusters.labels == label).sum()

        if number_of_photons_in_cluster <= max_multiplicity:
            counts[number_of_photons_in_cluster - 1] += 1
        else:
            print('Warning, found cluster of', number_of_photons_in_cluster, 'p.e, but max_multiplicity is only ', max_multiplicity)
    return counts


def finger_histogram_of_event(event, max_multiplicity=20):
    counts = np.zeros(max_multiplicity, dtype=np.int64)
    valid_time_lines = 0
    for time_line in event.photon_stream.time_lines:

        tl_counts = finger_histogram(time_line, max_multiplicity)

        if tl_counts[0] > 16 or tl_counts[1] > 8 or tl_counts[2] > 4 or tl_counts[3] > 2 or tl_counts[4] > 1:
            #print('Warning, time series is spooky', tl_counts)
            continue
        else:
            counts += tl_counts
            valid_time_lines += 1

    return {'counts': counts, 'valid_time_lines': valid_time_lines}


def finger_event(event, max_multiplicity=20):
    finger_event = {}
    finger_event['UnixTimeUTC'] = event.time.timestamp()
    finger_event['RUNID'] = event.run.id
    finger_event['EventNum'] = event.id
    finger_event['TriggerType'] = event.trigger_type
    finger_event['NIGHT'] = event.run.night

    fhist = finger_histogram_of_event(
        event=event,
        max_multiplicity=max_multiplicity)

    finger_event['1pe_multiplicity'] = fhist['counts'].tolist()
    finger_event['valid_pixels'] = fhist['valid_time_lines']
    return finger_event


def make_run_1pe_multiplicity(run, output_path, max_multiplicity=20):
    with open(output_path, 'w') as f:
        for event in tqdm.tqdm(run):
            f_evt = finger_event(event, max_multiplicity)
            f_evt_json = json.dumps(f_evt)
            f.write(f_evt_json+'\n')
