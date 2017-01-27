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

    info['photon_stream_exists'] = pd.Series(
        np.zeros(number_of_runs, dtype=np.bool), 
        index=info.index)

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
