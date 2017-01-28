import os
from fact import credentials
import pandas as pd
from . import tools
import numpy as np

drs_key = 2
observation_key = 1

def download_latest_runinfo():
    factdb = credentials.create_factdb_engine()
    print("Reading fresh RunInfo table, takes about 1min.")
    return pd.read_sql_table("RunInfo", factdb)

def read_runinfo_from_file(path='runinfo.msg'):
    return pd.read_msgpack(path)

def write_runinfo_to_file(runinfo, path='runinfo.msg'):
    runinfo.to_msgpack(path)

def get_runinfo():
    if os.path.exists('runinfo.msg'):
        return read_runinfo_from_file('runinfo.msg')
    else:
    	return download_latest_runinfo()


def observation_runs_in_runinfo_in_night_range(
    runinfo, 
    start_night=20110101, 
    end_night=20171231,
    only_a_fraction=1.0):
    past_start = (runinfo['fNight'] >= start_night).as_matrix()
    before_end = (runinfo['fNight'] < end_night).as_matrix()
    is_observation_run = (runinfo['fRunTypeKey'] == observation_key).as_matrix()
    valid = past_start*before_end*is_observation_run

    fraction = np.random.uniform(size=len(valid)) < only_a_fraction
    
    night_ids = runinfo['fNight'][valid*fraction]
    run_ids = runinfo['fRunID'][valid*fraction]

    jobs = []

    for i, run_id in enumerate(run_ids):
        jobs.append({
            'Night': night_ids.iloc[i],
            'Run': run_id})
    return jobs


def add_drs_run_info_to_jobs(runinfo, jobs):
    for job in jobs:   
        drs_run_candidates = runinfo[
            (runinfo.fNight == job["Night"])&
            (runinfo.fDrsStep == 2)&
            (runinfo.fRunTypeKey == 2)&
            (runinfo.fRunID < job["Run"])]
        
        if len(drs_run_candidates) >= 1:
            job["drs_Run"] = drs_run_candidates.iloc[-1].fRunID
            job["drs_file_name"] = '{bsn:08d}_{rrr:03d}.drs.fits.gz'.format(
                bsn=job['Night'],
                rrr=job["drs_Run"])
            job['drs_path'] = os.path.join(
                job['fact_dir'], 
                'raw', 
                job['yyyymmnn_dir'], 
                job['drs_file_name'])
        else:
            job["drs_Run"] = None
            job['drs_path'] = os.path.join(
                job['fact_dir'], 
                'no_corresponding_drs_file_found_in_runinfo_data_base.sorry')
    return jobs


def create_fake_fact_dir(path, runinfo):
    for index, row in runinfo.iterrows():
        night_id = runinfo['fNight'][index]
        run_id = runinfo['fRunID'][index]
        run_type_key = runinfo['fRunTypeKey'][index]

        yyyy = '{yyyy:04d}'.format(yyyy=tools.night_id_2_yyyy(night_id))
        mm = '{mm:02d}'.format(mm=tools.night_id_2_mm(night_id))
        nn = '{nn:02d}'.format(nn=tools.night_id_2_nn(night_id))
        os.makedirs(os.path.join(path, 'raw', yyyy, mm, nn), exist_ok=True)
        
        if run_type_key == drs_key:
            rrr = '{rrr:03d}'.format(rrr=run_id)
            fake_drs_path = os.path.join(path, 'raw', yyyy, mm, nn, yyyy+mm+nn+'_'+rrr+'.drs.fits.gz')
            with open(fake_drs_path, 'w') as drs_file:
                drs_file.write('I am a fake FACT drs file.')

        if run_type_key == observation_key:
            rrr = '{rrr:03d}'.format(rrr=run_id)
            fake_run_path = os.path.join(path, 'raw', yyyy, mm, nn, yyyy+mm+nn+'_'+rrr+'.fits.fz')
            with open(fake_run_path, 'w') as raw_file:
                raw_file.write('I am a fake FACT raw observation file.')