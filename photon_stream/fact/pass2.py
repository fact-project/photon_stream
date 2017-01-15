from .JsonLinesGzipReader import JsonLinesGzipReader
from ..._input_output import append_photonstream_to_binary_file
from ..._input_output import read_photonstream_from_raw_photonstream
import gzip
import json
import numpy as np

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
    evt_out['RunId'] = evt_in['RUNID'] 
    evt_out['NightId'] = evt_in['NIGHT']
    evt_out['EventId'] = evt_in['EventNum']
    evt_out['TriggerType'] = evt_in['TriggerType']
    evt_out['ZdPointing'] = evt_in['ZdPointing']
    evt_out['AzPointing'] = evt_in['AzPointing']
    evt_out['UnixTimeUTC'] = evt_in['UnixTimeUTC']

    if truncate_photon_stream: 
        ps = evt_in['PhotonArrivals']

        trunc_ps = []
        for pixel in ps:
            trunc_pixel = []
            for pulse_slice in pixel:
                pulse_time = pulse_slice*0.5e-9
                if pulse_time >= 15e-9 and pulse_time < 65e-9:
                    trunc_pixel.append(pulse_slice)
            trunc_ps.append(trunc_pixel)

        evt_out['PhotonStream'] = trunc_ps
    else:
        evt_out['PhotonStream'] = evt_in['PhotonArrivals']

    if not drop_baselinses:
        base_lines = evt_in['PhotonArrivalsBaseLine']
        comp_base_lines = []
        for base_line in base_lines:
            comp_base_lines.append(int(base_line*100))
        evt_out['BaseLines'] = comp_base_lines
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