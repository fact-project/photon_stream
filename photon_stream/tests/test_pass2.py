import numpy as np
import photon_stream as ps
import tempfile
import pkg_resources
import os

def test_fact_tools_pass2_jsonl_conversion():

    test_run_path = pkg_resources.resource_filename(
        'photon_stream', 
        'tests/resources/20151001_011_fact_tools_pass2_100_events.jsonl.gz')

    with tempfile.TemporaryDirectory(prefix='photon_stream_test_fact_tools_pass2') as tmp:
        tidy_run_path = os.path.join(tmp, '20151001_011.jsonl.gz')
        ps.fact.pass2.finalize_jsonl2jsonl(test_run_path, tidy_run_path)

        raw_run = ps.fact.JsonLinesGzipReader(test_run_path)
        tidy_run = ps.fact.JsonLinesGzipReader(tidy_run_path)

        for raw_event_dict in raw_run:
            tidy_event_dict = tidy_run.__next__()

            assert raw_event_dict['RUNID'] == tidy_event_dict['RUNID']
            assert raw_event_dict['NIGHT'] == tidy_event_dict['NIGHT']
            assert raw_event_dict['EventNum'] == tidy_event_dict['EventNum']
            assert raw_event_dict['TriggerType'] == tidy_event_dict['TriggerType']
            assert raw_event_dict['ZdPointing'] == tidy_event_dict['ZdPointing']
            assert raw_event_dict['AzPointing'] == tidy_event_dict['AzPointing']
            assert raw_event_dict['ZdPointing'] == tidy_event_dict['ZdPointing']
            assert raw_event_dict['UnixTimeUTC'][0] == tidy_event_dict['UnixTimeUTC'][0]
            assert raw_event_dict['UnixTimeUTC'][1] == tidy_event_dict['UnixTimeUTC'][1]

            assert 'SliceDuration' not in raw_event_dict
            assert 'SliceDuration' in tidy_event_dict
            assert tidy_event_dict['SliceDuration'] == 0.5e-9

            assert len(raw_event_dict['PhotonArrivals']) == len(tidy_event_dict['PhotonArrivals'])
            assert 1440 == len(raw_event_dict['PhotonArrivals']) 
            assert 1440 == len(tidy_event_dict['PhotonArrivals'])

            for pixel in range(1440):
                for pulse in range(len(raw_event_dict['PhotonArrivals'][pixel])):
                    assert raw_event_dict['PhotonArrivals'][pixel][pulse] == tidy_event_dict['PhotonArrivals'][pixel][pulse]

            assert 'PhotonArrivalsBaseLine100' not in raw_event_dict
            assert 'PhotonArrivalsBaseLine100' in tidy_event_dict

            assert 'PhotonArrivalsBaseLine' not in tidy_event_dict
            assert 'PhotonArrivalsBaseLine' in raw_event_dict

            assert len(raw_event_dict['PhotonArrivalsBaseLine']) == len(tidy_event_dict['PhotonArrivalsBaseLine100'])
            assert 1440 == len(raw_event_dict['PhotonArrivalsBaseLine']) 
            assert 1440 == len(tidy_event_dict['PhotonArrivalsBaseLine100'])            

            for pixel in range(1440):
                raw_baseline = int(100.0*raw_event_dict['PhotonArrivalsBaseLine'][pixel])
                assert raw_baseline == tidy_event_dict['PhotonArrivalsBaseLine100'][pixel]