import os
from os.path import abspath
from os.path import join
from os.path import exists
from tqdm import tqdm
import pandas as pd
import numpy as np
import fact
import filelock

from . import runinfo as ri
from .runinfo import ID_RUNINFO_KEYS
from . import tools
from .runinfo2runstatus import runinfo2runstatus


def read(path):
    return ri.read(path)


def init(obs_dir, latest_runstatus=None):
    """
    Initializes phs/obs/ and the runstatus.csv
    """
    runstatus_lock_path = join(obs_dir, '.lock.runstatus.csv')
    runstatus_path = join(obs_dir, 'runstatus.csv')
    assert not exists(runstatus_path)
    assert not exists(runstatus_lock_path)
    if not os.path.exists(runstatus_path):
        os.makedirs(obs_dir, exist_ok=True, mode=0o777)
        if latest_runstatus is None:
            latest_runstatus = _download_latest()
        ri.write(latest_runstatus, runstatus_path)
    tools.touch(runstatus_lock_path)


def update_to_latest(obs_dir, latest_runstatus=None, lock_timeout=1):
    """
    Update obs_dir/runstatus.csv to the latest version from FACT on La Palma.
    """
    runstatus_path = join(obs_dir, 'runstatus.csv')
    if latest_runstatus is None:
        latest_runstatus = _download_latest()

    lock = filelock.FileLock(join(obs_dir, '.lock.runstatus.csv'))
    with lock.acquire(timeout=lock_timeout):
        runstatus = read(runstatus_path)
        new_runstatus = _append_new_runstatus(runstatus, latest_runstatus)
        ri.write(new_runstatus, runstatus_path)
    return new_runstatus


def _append_new_runstatus(old_runstatus, new_runstatus):
    ors = old_runstatus.set_index(ID_RUNINFO_KEYS)
    nrs = new_runstatus.set_index(ID_RUNINFO_KEYS)
    nrs.loc[ors.index] = ors
    return nrs.reset_index()


def _download_latest():
    """
    Download the latest runinfo from FACT on La Palma and convert it to
    a runstatus.

    Return
    ------
    runstatus: pd.DataFrame
        A fresh runstatus table with all photon-stream fields set to nan.
    """
    return runinfo2runstatus(ri.download_latest())