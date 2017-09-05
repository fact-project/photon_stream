from os.path import join
from os.path import exists
import os
from filelock import FileLock
from filelock import Timeout
from glob import glob
import json
import pandas as pd
import numpy as np
from .. import runstatus as rs
from .. import runinfo as ri
from .qstat import qstat
from fact.path import template_to_path
from fact.path import tree_path
from .qsub import qsub
from shutil import which

QSUB_OBS_STATUS_NAME_PREFIX = 'phs_obs_status'


def status(
    obs_dir=join('/gpfs0','fact','processing','public','phs','obs'),
    max_jobs_in_qsub=256,
    queue='fact_medium',
):
    print('Start status in '+obs_dir)

    runstatus_path = join(obs_dir,'runstatus.csv')
    runstatus_lock_path = join(obs_dir,'.lock.runstatus.csv')
    tmp_status_dir = join(obs_dir,'.tmp_status')
    obs_std_dir = obs_dir+'.std'

    assert exists(runstatus_path)
    assert exists(runstatus_lock_path)
    os.makedirs(tmp_status_dir, exist_ok=True)

    print('Try to lock '+runstatus_path)

    try:
        runstatus_lock = FileLock(runstatus_lock_path)
        with runstatus_lock.acquire(timeout=1):
            print(runstatus_path+' is locked now')

            tmp_status = read_and_remove_tmp_status(tmp_status_dir)
            runstatus = rs.read(runstatus_path)
            runstatus = add_tmp_status_to_runstatus(tmp_status, runstatus)
            ri.write(runstatus, runstatus_path)

            print('Add '+str(len(tmp_status))+' new stati to '+runstatus_path)

            no_status_yet = runstatus[np.isnan(runstatus.PhsSize)]
            rs_qstat = qstat(is_in_JB_name=QSUB_OBS_STATUS_NAME_PREFIX)
            no_status_yet = ri.remove_from_first_when_also_in_second(
                first=no_status_yet,
                second=rs_qstat,
            )
            no_status_yet.sort_values(
                by=ri.ID_RUNINFO_KEYS , 
                inplace=True,
                ascending=False
            )  
            num_runs_for_qsub = max_jobs_in_qsub - len(rs_qstat)

            print('Submitt '+str(num_runs_for_qsub)+' new status requests ...')

            i = 0
            for index, row in no_status_yet.iterrows():
                if i > num_runs_for_qsub:
                    break
                i += 1

                fNight = int(np.round(row.fNight))
                fRunID = int(np.round(row.fRunID))
                job = {
                    'name': template_to_path(fNight, fRunID, QSUB_OBS_STATUS_NAME_PREFIX+'_{N}_{R}'),
                    'o_path': tree_path(fNight, fRunID, prefix=tmp_status_dir, suffix='.o'),
                    'e_path': tree_path(fNight, fRunID, prefix=tmp_status_dir, suffix='.e'),
                    '--phs_path': tree_path(fNight, fRunID, prefix=obs_dir, suffix='.phs.jsonl.gz'),
                    '--status_path': tree_path(fNight, fRunID, prefix=tmp_status_dir, suffix='.json'),
                    '--phs_o_path': tree_path(fNight, fRunID, prefix=obs_std_dir, suffix='.o'),
                    '--phs_e_path': tree_path(fNight, fRunID, prefix=obs_std_dir, suffix='.e'),
                }
                qsub(
                    job=job, 
                    exe_path=which('phs.isdc.obs.status.worker'),
                    queue=queue
                )
            print('Submission done')
    except Timeout:
        print('Could not get the lock on '+runstatus_path)
    print('End')

def read_and_remove_tmp_status(tmp_status_dir):
    tmp_status_paths = glob(join(tmp_status_dir,'*','*','*','*.json'))
    tmp_status_list = []
    for tmp_status_path in tmp_status_paths:
        with open(tmp_status_path, 'rt') as fin:
            tmp_status_list.append(json.loads(fin.read()))
        os.remove(tmp_status_path)
    if len(tmp_status_list) > 0:
        tmp_stauts = pd.DataFrame(tmp_status_list)
    else:
        tmp_stauts = pd.DataFrame(columns=ri.RUNSTATUS_KEYS)
    tmp_stauts.sort_values(by=ri.ID_RUNINFO_KEYS , inplace=True)
    return tmp_stauts


def add_tmp_status_to_runstatus(tmp_status, runstatus):
    irs = runstatus.set_index(ri.ID_RUNINFO_KEYS)
    for i, row in tmp_status.iterrows():
        for key in ri.PHS_STATUS_KEYS:
            irs.set_value((row['fNight'], row['fRunID']), key, row[key])
    return irs.reset_index()
