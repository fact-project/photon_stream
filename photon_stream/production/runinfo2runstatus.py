from .drs_run import assign_drs_runs
from .runinfo import RUNSTATUS_KEYS
from .runinfo import OBSERVATION_RUN_TYPE_KEY
from .runinfo import TRIGGER_NUMBER_RUNINFO_KEYS
import pandas as pd
import numpy as np


def runinfo2runstatus(runinfo):
    ri = runinfo.copy()
    ri = assign_drs_runs(ri)
    ri = drop_not_obs_runs(ri)
    ri = add_expected_phs_event_column(ri)
    ri = add_empty_runstatus_columns(ri)
    ri['StatusIteration'] = pd.Series(0, index=riout.index)
    ri['IsOk'] = pd.Series(0, index=riout.index)
    return drop_not_matching_keys(ri, RUNSTATUS_KEYS)


def drop_not_obs_runs(runinfo):
    return runinfo[
        runinfo.fRunTypeKey==OBSERVATION_RUN_TYPE_KEY
    ].copy()


def add_expected_phs_event_column(runinfo):
    riout = runinfo.copy()
    riout['NumExpectedPhsEvents'] = pd.Series(
        number_expected_phs_events(riout), 
        index=riout.index
    )
    return riout


def number_expected_phs_events(runinfo):
    count = np.zeros(runinfo.shape[0])
    for key in TRIGGER_NUMBER_RUNINFO_KEYS:
        count += runinfo[key]
    count[runinfo['fRunTypeKey'] != OBSERVATION_RUN_TYPE_KEY] = np.nan
    return count


def add_empty_runstatus_columns(runinfo):
    riout = runinfo.copy()
    for phs_key in RUNSTATUS_KEYS:
        if phs_key not in riout:
            riout[phs_key] = pd.Series(np.nan, index=riout.index)
    return riout


def drop_not_matching_keys(runinfo, desired_keys):
    riout = runinfo.copy()
    for key in riout.keys():
        if key not in desired_keys:
            riout.drop(key, axis=1, inplace=True)
    return riout
