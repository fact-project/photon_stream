import os
from tqdm import tqdm
import pandas as pd
import numpy as np

from . import runinfo
from . import tools


def status(photon_stream_dir, known_runs_database='known_runs.msg'):
    info_path = os.path.abspath(
	os.path.join(photon_stream_dir, known_runs_database))
    try:
        info = runinfo.read_runinfo_from_file(info_path)
    except:
        info = runinfo.download_latest_runinfo()
    number_of_runs = len(info['fRunID'])

    if 'photon_stream_exists' not in info:
        info['photon_stream_exists'] = pd.Series(
            np.zeros(number_of_runs, dtype=np.bool), 
            index=info.index)
    if 'photon_stream_NumTrigger' not in info:
        info['photon_stream_NumTrigger'] = pd.Series(
            np.zeros(number_of_runs, dtype=np.int), 
            index=info.index)

    for index, row in tqdm(info.iterrows()):
        night = info['fNight'][index]
        run = info['fRunID'][index]

        if info['fRunTypeKey'][index] == runinfo.observation_key:
            if info['photon_stream_NumTrigger'][index]==0:
                file_name = '{yyyymmnn:08d}_{rrr:03d}.phs.jsonl.gz'.format(
                    yyyymmnn=night,
                    rrr=run)

                run_path = os.path.join(
                    photon_stream_dir, 
                    '{yyyy:04d}'.format(yyyy=tools.night_id_2_yyyy(night)), 
                    '{mm:02d}'.format(mm=tools.night_id_2_mm(night)), 
                    '{nn:02d}'.format(nn=tools.night_id_2_nn(night)), 
                    file_name)

                if os.path.exists(run_path):    
                    info.set_value(index, 'photon_stream_exists', True) 
                    info.set_value(index, 'photon_stream_NumTrigger', tools.number_of_events_in_run(run_path))
                    print('New run '+str(night)+' '+str(run)+' '+str(info['photon_stream_NumTrigger'][index])+' trigger.')

    runinfo.write_runinfo_to_file(info, info_path)


def print_status_in_range(start_night, end_night, info):
    past_start = info['fNight'] >= start_night
    before_end = info['fNight'] < end_night
    is_observation_run = info['fRunTypeKey'] == runinfo.observation_key

    in_range = past_start*before_end*is_observation_run

    night_ids = info['fNight'][in_range]
    run_ids = info['fRunID'][in_range]
    expected_triggers = (
        info['fNumExt1Trigger'][in_range] + 
        info['fNumExt2Trigger'][in_range] + 
        info['fNumPhysicsTrigger'][in_range] + 
        info['fNumPedestalTrigger'][in_range])
    actual_triggers = info['photon_stream_NumTrigger'][in_range]
    exisences = info['photon_stream_exists'][in_range]
    completation_ratios = actual_triggers/expected_triggers

    print(' night  run  expected_events actualevents complete_ratio')
    for i, run_id in enumerate(run_ids):
        print('{night:08d} {rrr:03d} {expected_evts:>6d} {actual_evts:>6d} '.format(
            night=night_ids.iloc[i],  
            rrr=run_ids.iloc[i],
            expected_evts=int(expected_triggers.iloc[i]),
            actual_evts=int(actual_triggers.iloc[i]),
            )+progress(completation_ratios.iloc[i]))

def progress(ratio, length=20):
    try:
        prog = int(np.round(ratio*length))
        percent = np.round(ratio*100)
    except ValueError:
        prog = 0
        percent = 0
    out = '|'
    for p in range(prog):
        out += '|'
    out += ' '+str(int(percent))+'%'
    return out
