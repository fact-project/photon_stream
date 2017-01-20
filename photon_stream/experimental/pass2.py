from ..JsonLinesGzipReader import JsonLinesGzipReader
from ..PhotonStream import truncate_time_lines
import gzip
import json

# Size test 20151001_11, 12309 events [MByte]
#               raw   15-65ns     15-65ns 
#                                 no baseline
# -------------------------------------------------------
# zfits        2935       -        -
# jsonl.gz.ft   302       -        - 
# jsonl.gz      154      94       69 
# 1pe.gz        123      79       55

# speed test, copx event ids into list [events/s]
#               raw   15-65ns     15-65ns 
#                                 no baseline
# -------------------------------------------------------
# zfits           -       -        -
# jsonl.gz.ft     -       -        - 
# jsonl.gz        -       -        - 
# 1pe           121       -        -


def reduce_event(
    evt_in, 
    truncate_photon_stream=False, 
    drop_baselinses=False):

    evt_out = {}
    evt_out['RUNID'] = evt_in['RUNID'] 
    evt_out['NIGHT'] = evt_in['NIGHT']
    evt_out['EventNum'] = evt_in['EventNum']
    evt_out['TriggerType'] = evt_in['TriggerType']
    evt_out['ZdPointing'] = evt_in['ZdPointing']
    evt_out['AzPointing'] = evt_in['AzPointing']
    evt_out['UnixTimeUTC'] = evt_in['UnixTimeUTC']
    evt_out['SliceDuration'] = 0.5e-9

    if truncate_photon_stream: 
        evt_out['PhotonArrivals'] = truncate_time_lines(
            evt_in['PhotonArrivals'], 
            slice_duration=evt_out['SliceDuration'],
            start_time=15e-9, 
            end_time=65e-9)
    else:
        evt_out['PhotonArrivals'] = evt_in['PhotonArrivals']

    if not drop_baselinses:
        base_lines = evt_in['PhotonArrivalsBaseLine']
        comp_base_lines = []
        for base_line in base_lines:
            comp_base_lines.append(int(base_line*100))
        evt_out['PhotonArrivalsBaseLine100'] = comp_base_lines
    return evt_out


def finalize_jsonl2jsonl(
    inpath, 
    outpath, 
    truncate_photon_stream=False, 
    drop_baselinses=False):

    """
    Compress the original fact_tools output further by reducing the precision on
    the PhotonArrivalsBaseLine. Also remove whitespaces.

    Parameters
    ----------
    inpath      path to the fact-tools output json.gz file

    output      path to the new and smaller output jsonl.gz file 
    """
    fin = JsonLinesGzipReader(inpath)
    with gzip.open(outpath, 'wt') as fout:
        for evt_in in fin:
            
            evt_out = reduce_event(
                evt_in=evt_in,
                truncate_photon_stream=truncate_photon_stream,
                drop_baselinses=drop_baselinses)

            event_line = json.dumps(evt_out, separators=(',', ':'))
            fout.write(event_line+'\n')