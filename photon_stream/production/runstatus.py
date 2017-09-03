import os
from os.path import abspath
from os.path import join
from os.path import exists
from tqdm import tqdm
import pandas as pd
import numpy as np
import fact
import filelock

from . import runinfo
from . import tools


def read(obs_dir):
    runstatus_path = join(obs_dir, 'runstatus.csv')
    return runinfo.read(runstatus_path)


def init_runstatus(obs_dir, latest_runstatus=None):
    runstatus_lock_path = join(obs_dir, '.lock.runstatus.csv')
    runstatus_path = join(obs_dir, 'runstatus.csv')

    assert not exists(runstatus_lock_path)
    if not os.path.exists(runstatus_path):
        os.makedirs(obs_dir, exist_ok=True, mode=0o777)
        if latest_runstatus is None:
            latest_runstatus = runinfo.latest_runstatus()
        runinfo.write(latest_runstatus, runstatus_path)
    tools.touch(runstatus_lock_path)


def update_to_latest(obs_dir, latest_runstatus=None):
    runstatus_path = join(obs_dir, 'runstatus.csv')
    if latest_runstatus is None:
        latest_runstatus = runinfo.latest_runstatus()

    lock = filelock.FileLock(join(obs_dir, '.lock.runstatus.csv'))
    with lock.acquire(timeout=1):
        runstatus = runinfo.read(runstatus_path)
        new_runstatus = runinfo.append_new_runstatus(runstatus, latest_runstatus)
        runinfo.write(new_runstatus, runstatus_path)
    return new_runstatus


def update_phs_status(obs_dir, skip_NumActualPhsEvents=False):
    runstatus_path = join(obs_dir, 'runstatus.csv')

    lock = filelock.FileLock(join(obs_dir, '.lock.runstatus.csv'))
    with lock.acquire(timeout=1):
        runstatus = runinfo.read(runstatus_path)
        runstatus = run_update(
            runstatus=runstatus,
            obs_dir=obs_dir,
            skip_NumActualPhsEvents=skip_NumActualPhsEvents
        )
        runinfo.write(runstatus, runstatus_path)
    return runstatus


def run_update(runstatus, obs_dir, skip_NumActualPhsEvents=False):
    """
    Returns an updated runstatus
    """
    rs = runstatus.copy()

    for index, row in tqdm(rs.iterrows()):
        night = int(row.fNight)
        run = row.fRunID

        if np.isnan(row['NumActualPhsEvents']) and not skip_NumActualPhsEvents:
            run_path = fact.path.tree_path(
                night, run, prefix=obs_dir, suffix='.phs.jsonl.gz'
            )
            if exists(run_path):
                actual_events = 0
                try:
                    actual_events = tools.number_of_events_in_file(run_path)
                except:
                    pass
                rs.loc[index, 'NumActualPhsEvents'] = actual_events

        if np.isnan(row['StdOutSize']):
            stdo_path = fact.path.tree_path(
                night, run, prefix=obs_dir+'.std', suffix='.o'
            )
            if exists(stdo_path):
                rs.loc[index, 'StdOutSize'] = os.stat(stdo_path).st_size

        if np.isnan(row['StdErrorSize']):
            stde_path = fact.path.tree_path(
                night, run, prefix=obs_dir+'.std', suffix='.e'
            )
            if exists(stde_path):
                rs.loc[index, 'StdErrorSize'] = os.stat(stde_path).st_size

        if row['NumActualPhsEvents'] == row['NumExpectedPhsEvents']:
            rs.loc[index, 'IsOk'] = 1
    return rs