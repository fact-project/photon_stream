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
from ...EventListReader import EventListReader
from .qstat import qstat
from fact.path import template_to_path
from fact.path import tree_path
from .qsub import qsub
from .qsub import QUEUE_NAME
from shutil import which
import shutil

QSUB_OBS_STATUS_PREFIX = 'phs_obs_status'


def status(
    obs_dir=join('/gpfs0','fact','processing','public','phs','obs'),
    max_jobs_in_qsub=256,
    queue=QUEUE_NAME,
    runs_in_qstat=None
):
    print('Start status')

    runstatus_path = join(obs_dir,'runstatus.csv')
    runstatus_lock_path = join(obs_dir,'.lock.runstatus.csv')
    tmp_status_dir = join(obs_dir,'.tmp_status')
    obs_std_dir = obs_dir+'.std'

    assert exists(runstatus_path)
    assert exists(runstatus_lock_path)
    os.makedirs(tmp_status_dir, exist_ok=True)

    try:
        runstatus_lock = FileLock(runstatus_lock_path)
        with runstatus_lock.acquire(timeout=1):
            print('runstatus.csv is locked')

            tmp_status = read_and_remove_tmp_status(tmp_status_dir)
            runstatus = rs.read(runstatus_path)
            runstatus = add_tmp_status_to_runstatus(tmp_status, runstatus)
            ri.write(runstatus, runstatus_path)

            print('Add '+str(len(tmp_status))+' new stati')

            runs_to_be_checked_now, runstatus = runs_to_be_checked_now_and_incremented_runstatus(
                runstatus
            )

            print(len(runstatus)-len(runs_to_be_checked_now),'are not checked again')

            if runs_in_qstat is None:
                runs_in_qstat = qstat(is_in_JB_name=QSUB_OBS_STATUS_PREFIX)

            runs_to_be_checked_now = ri.remove_from_first_when_also_in_second(
                first=runs_to_be_checked_now,
                second=runs_in_qstat,
            )

            print(len(runs_to_be_checked_now),'runs are checked now')
            
            num_runs_for_qsub = max_jobs_in_qsub - len(runs_in_qstat)
            runstatus = runstatus.set_index(ri.ID_RUNINFO_KEYS)

            i = 0
            for index, row in runs_to_be_checked_now.iterrows():
                if i > num_runs_for_qsub:
                    break

                fNight = int(np.round(row.fNight))
                fRunID = int(np.round(row.fRunID))

                # StdOutSize and StdErrorSize
                #----------------------------
                o_path = tree_path(fNight, fRunID, prefix=obs_std_dir, suffix='.o')
                o_size = np.nan
                if exists(o_path):
                    o_size = os.stat(o_path).st_size
                runstatus.set_value((fNight, fRunID), 'StdOutSize', o_size)
                e_path = tree_path(fNight, fRunID, prefix=obs_std_dir, suffix='.e')
                e_size = np.nan
                if exists(e_path):
                    e_size = os.stat(e_path).st_size
                runstatus.set_value((fNight, fRunID), 'StdErrorSize', e_size)


                # PhsSize and NumActualPhsEvents
                #-------------------------------
                phs_path = tree_path(fNight, fRunID, prefix=obs_dir, suffix='.phs.jsonl.gz')
                if np.isnan(row.PhsSize):
                    if exists(phs_path):
                        phs_size = os.stat(phs_path).st_size
                        runstatus.set_value((fNight, fRunID), 'PhsSize', phs_size)
                        # Submitt the intense task of event counting to qsub, and 
                        # collect the output next time in phs/obs/.tmp_status
                        job = {
                            'name': template_to_path(fNight, fRunID, QSUB_OBS_STATUS_PREFIX+'_{N}_{R}'),
                            'o_path': None, #tree_path(fNight, fRunID, tmp_status_dir, '.o'),
                            'e_path': None, #tree_path(fNight, fRunID, tmp_status_dir, '.e'),
                            '--phs_path': phs_path,
                            '--status_path': tree_path(fNight, fRunID, prefix=tmp_status_dir, suffix='.json'),
                        }
                        qsub(
                            job=job, 
                            exe_path=which('phs.isdc.obs.status.worker'),
                            queue=queue
                        )
                        i += 1
                    else:
                        runstatus.set_value((fNight, fRunID), 'PhsSize', np.nan)
                        runstatus.set_value((fNight, fRunID), 'NumActualPhsEvents', np.nan)

                runstatus.set_value((fNight, fRunID), 'StatusIteration', row['StatusIteration'] + 1)

            runstatus = runstatus.reset_index()
            runstatus['StatusIteration'] -= runstatus['StatusIteration'].min()
            runstatus = set_is_ok(runstatus)
            ri.write(runstatus, runstatus_path)
            print(i, 'status requests submitted to qsub')
    except Timeout:
        print('Could not get the lock on '+runstatus_path)
    print('End')


def runs_to_be_checked_now_and_incremented_runstatus(runstatus):
    runstatus = runstatus.copy()
    max_it = runstatus['StatusIteration'].max()
    all_at_max_it = np.all(runstatus['StatusIteration'] == max_it)
    if all_at_max_it:
        it_for_runs_not_checked_yet = max_it + 1
    else:
        it_for_runs_not_checked_yet = max_it

    nanPhsSize = np.isnan(runstatus.PhsSize)
    runs_to_be_checked_now = runstatus[nanPhsSize]
    raw_StatusIteration = runstatus['StatusIteration'].values
    raw_StatusIteration[np.invert(nanPhsSize)] = it_for_runs_not_checked_yet
    runstatus['StatusIteration'] = pd.Series(raw_StatusIteration, index=runstatus.index)
    return runs_to_be_checked_now, runstatus


def read_and_remove_tmp_status(tmp_status_dir):
    tmp_status_list = []
    for tmp_status_path in glob(join(tmp_status_dir,'*','*','*','*.json')):
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
        irs.set_value((row['fNight'], row['fRunID']), 'NumActualPhsEvents', row['NumActualPhsEvents'])
    return irs.reset_index()


def set_is_ok(runstatus):
    rs = runstatus.copy()
    actual_eq_expected = (
        rs['NumActualPhsEvents'] == rs['NumExpectedPhsEvents']
    )
    rs.loc[actual_eq_expected, 'IsOk'] = 1
    return rs