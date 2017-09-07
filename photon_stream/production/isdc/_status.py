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
from shutil import which
import shutil

QSUB_OBS_STATUS_NAME_PREFIX = 'phs_obs_status'


def status(
    obs_dir=join('/gpfs0','fact','processing','public','phs','obs'),
    max_jobs_in_qsub=256,
    queue='fact_medium',
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

            max_it = max_status_iteration(runstatus)
            all_at_max_it = np.all(runstatus['StatusIteration']==max_it)
            if all_at_max_it:
                it_for_not_checked = max_it + 1
            else:
                it_for_not_checked = max_it

            nanPhsSize = np.isnan(runstatus.PhsSize)
            no_status_yet = runstatus[nanPhsSize]
            raw_status_iteration = runstatus['StatusIteration'].values
            raw_status_iteration[np.invert(nanPhsSize)] = it_for_not_checked 
            runstatus['StatusIteration'] = pd.Series(raw_status_iteration, index=runstatus.index)

            print(np.invert(nanPhsSize).sum(),'are not checked again')
            print(len(no_status_yet),'runs are checked now')

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
            max_it = max_status_iteration(runstatus)
            if np.all(runstatus['StatusIteration'] == max_it):
                to_be_ckecked_now = no_status_yet
            else:
                to_be_ckecked_now = no_status_yet[no_status_yet['StatusIteration'] < max_it]

            print(len(to_be_ckecked_now), 'runs with priority')

            num_runs_for_qsub = max_jobs_in_qsub - len(rs_qstat)

            runstatus = runstatus.set_index(ri.ID_RUNINFO_KEYS)

            i = 0
            for index, row in to_be_ckecked_now.iterrows():
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
                    if exists_and_first_event_can_be_read(phs_path):
                        # Submitt the intense task of event counting to qsub, and 
                        # collect the output next time in phs/obs/.tmp_status
                        job = {
                            'name': template_to_path(fNight, fRunID, QSUB_OBS_STATUS_NAME_PREFIX+'_{N}_{R}'),
                            'o_path': tree_path(fNight, fRunID, tmp_status_dir, '.o'),
                            'e_path': tree_path(fNight, fRunID, tmp_status_dir, '.e'),
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
            ri.write(runstatus, runstatus_path)
            print(i, 'status requests submitted to qsub')
    except Timeout:
        print('Could not get the lock on '+runstatus_path)
    print('End')


def exists_and_first_event_can_be_read(phs_path):
    if exists(phs_path):
        can_be_read = False
        try:
            event_list = EventListReader(phs_path)
            first_event = next(event_list)
            can_be_read = True
        except:
            pass
        return can_be_read
    else:
        return False


def read_and_remove_tmp_status(tmp_status_dir):
    tmp_status_paths = glob(join(tmp_status_dir,'*','*','*','*.json'))
    tmp_status_list = []
    for tmp_status_path in tmp_status_paths:
        with open(tmp_status_path, 'rt') as fin:
            tmp_status_list.append(json.loads(fin.read()))
        #os.remove(tmp_status_path)
        shutil.move(tmp_status_path, tmp_status_path+'.u')
    if len(tmp_status_list) > 0:
        tmp_stauts = pd.DataFrame(tmp_status_list)
    else:
        tmp_stauts = pd.DataFrame(columns=ri.RUNSTATUS_KEYS)
    tmp_stauts.sort_values(by=ri.ID_RUNINFO_KEYS , inplace=True)
    return tmp_stauts


def add_tmp_status_to_runstatus(tmp_status, runstatus):
    irs = runstatus.set_index(ri.ID_RUNINFO_KEYS)
    for i, row in tmp_status.iterrows():
        for key in ['PhsSize', 'NumActualPhsEvents']:
            irs.set_value((row['fNight'], row['fRunID']), key, row[key])
    return irs.reset_index()


def max_status_iteration(runstatus):
    return int(np.round(runstatus['StatusIteration'].max()))

