import os
from fact import credentials
import pandas as pd


def get_fresh_runinfo():
    factdb = credentials.create_factdb_engine()
    print("Reading fresh RunInfo table, takes about 1min.")
    runinfo = pd.read_sql_table("RunInfo", factdb)
    with pd.HDFStore('runinfo.h5') as store:
        store.put("runinfo", runinfo)
    return runinfo


def get_runinfo():
    if os.path.exists('runinfo.h5'):
        with pd.HDFStore('runinfo.h5') as store:
            return store["runinfo"]
    else:
    	return get_fresh_runinfo()


def observation_runs_in_runinfo_in_night_range(
    runinfo, 
    start_nigth=20110101, 
    end_nigth=20171231):
    jobs = []

    observation_key = 1
    for index, row in runinfo.iterrows():
        night_id = runinfo['fNight']
        run_id = runinfo['fRunID']
        run_type_key = runinfo['fRunTypeKey']
        if night_id >= start_nigth and night_id < end_nigth and run_type_key == observation_key:
            jobs.append({
                'Night': night_id,
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
                job['rel_path'], 
                job['drs_file_name'])
        else:
            job["drs_Run"] = None
    return jobs