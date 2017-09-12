"""
DRS runs are calibration runs performed by FACT to calibrate the 
Domini Ring Sampler (DRS4) which samples the electric input signal with 2 Giga
samples per second. To convert a raw run into a photon-stream run, the raw run
first needs to be calibrated using a DRS run. So each observation raw run 
is assigned the latest DRS run.
"""
import warnings
import numpy as np
import pandas as pd
from .runinfo import ID_RUNINFO_KEYS
from .runinfo import DRS_RUN_TYPE_KEY
from .runinfo import DRS_STEP_KEY


def _drs_fRunID_for_obs_run(runinfo, fNight, fRunID):
    warnings.warn(
        'This drs run locater function was replaced with "assign_drs_runs()"'
        'This function is still kept for unit testing the new one.', 
        DeprecationWarning
    )

    ri = runinfo.copy()
    ri.sort_values(inplace=True, ascending=False, by=ID_RUNINFO_KEYS)
    
    drs_candidates = ri[
        (ri.fNight == fNight)&
        (ri.fDrsStep == DRS_STEP_KEY)&
        (ri.fRunTypeKey == DRS_RUN_TYPE_KEY)&
        (ri.fRunID < fRunID)
    ]
    if len(drs_candidates) >= 1:
        return drs_candidates.iloc[0].fRunID
    else:
        return np.nan


def assign_drs_runs(runinfo):
    """
    Returns a runinfo with a new column 'DrsRunID' where the DRS run ids for
    all observation runs are listed.
    """
    ri = runinfo.copy()
    ri.sort_values(inplace=True, ascending=True, by=ID_RUNINFO_KEYS)

    ri.insert(loc=2, column='DrsRunID', value=pd.Series(np.nan, index=ri.index))
    raw = ri.as_matrix()
    k = {}
    for c, key in enumerate(ri.keys()):
        k[key] = c
    current_drs_fRunID = np.nan
    current_drs_fNight = np.nan
    for i in range(raw.shape[0]):
        if (
            raw[i,k['fRunTypeKey']]==DRS_RUN_TYPE_KEY and 
            raw[i,k['fDrsStep']]==DRS_STEP_KEY
        ):
            current_drs_fRunID = raw[i,k['fRunID']]
            current_drs_fNight = raw[i,k['fNight']]
        else:
            if current_drs_fNight == raw[i,k['fNight']]:
                raw[i,k['DrsRunID']] = current_drs_fRunID
    ri = pd.DataFrame(raw, columns=ri.keys().tolist())
    ri.sort_values(inplace=True, ascending=False, by=ID_RUNINFO_KEYS)
    return ri