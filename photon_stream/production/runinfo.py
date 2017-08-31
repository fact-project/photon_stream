import os
from fact import credentials
import pandas as pd
from . import tools
import numpy as np


DRS_RUN_TYPE_KEY = 2

OBSERVATION_RUN_TYPE_KEY = 1

ID_RUNINFO_KEYS = [
    'fNight',
    'fRunID',
]

TYPE_RUNINFO_KEYS = ['fRunTypeKey']

TRIGGER_NUMBER_RUNINFO_KEYS = [
    'fNumExt1Trigger',
    'fNumExt2Trigger',
    'fNumPhysicsTrigger',
    'fNumPedestalTrigger',
]

DRS_TYPE_RUNINFO_KEYS = ['fDrsStep']

PHS_RUNINFO_KEYS = [
    'PhotonStreamNumEvents',
]

RUNINFO_KEYS = (
    ID_RUNINFO_KEYS +
    TYPE_RUNINFO_KEYS +
    TRIGGER_NUMBER_RUNINFO_KEYS +
    DRS_TYPE_RUNINFO_KEYS
)

RUNSTATUS_KEYS = (
    ID_RUNINFO_KEYS +
    PHS_RUNINFO_KEYS
)


def download_latest():
    factdb = credentials.create_factdb_engine()
    print("Reading fresh RunInfo table, takes about 1min.")
    return pd.read_sql_table(
        table_name="RunInfo",
        con=factdb,
        columns=RUNINFO_KEYS
    )

def read(path='phs_runstatus.csv'):
    return pd.read_csv(path)

def write(runinfo, path='phs_runstatus.csv'):
    runinfo.to_csv(path, index=False, na_rep='nan')


def create_fake_fact_dir(path, runinfo):
    for index, row in runinfo.iterrows():
        night_id = runinfo['fNight'][index]
        run_id = runinfo['fRunID'][index]
        run_type_key = runinfo['fRunTypeKey'][index]

        yyyy = '{yyyy:04d}'.format(yyyy=tools.night_id_2_yyyy(night_id))
        mm = '{mm:02d}'.format(mm=tools.night_id_2_mm(night_id))
        nn = '{nn:02d}'.format(nn=tools.night_id_2_nn(night_id))
        os.makedirs(os.path.join(path, 'raw', yyyy, mm, nn), exist_ok=True, mode=0o777)
        
        if run_type_key == DRS_RUN_TYPE_KEY:
            rrr = '{rrr:03d}'.format(rrr=run_id)
            fake_drs_path = os.path.join(path, 'raw', yyyy, mm, nn, yyyy+mm+nn+'_'+rrr+'.drs.fits.gz')
            with open(fake_drs_path, 'w') as drs_file:
                drs_file.write('I am a fake FACT drs file.')

        if run_type_key == OBSERVATION_RUN_TYPE_KEY:
            rrr = '{rrr:03d}'.format(rrr=run_id)
            fake_run_path = os.path.join(path, 'raw', yyyy, mm, nn, yyyy+mm+nn+'_'+rrr+'.fits.fz')
            with open(fake_run_path, 'w') as raw_file:
                raw_file.write('I am a fake FACT raw observation file.')


def runinfo_only_with_keys(runinfo, desired_keys):
    ri_out = runinfo.copy()
    for key in ri_out.keys():
        if key not in desired_keys:
            ri_out.drop(key, axis=1, inplace=True)
    return ri_out


def append_runinfo_to_known_runs(runinfo, known_runs):
    phs_info = runinfo_only_with_keys(
        runinfo=known_runs,
        desired_keys=ID_RUNINFO_KEYS + PHS_RUNINFO_KEYS,
    )
    new_known_runs = runinfo.merge(phs_info, how='left', on=ID_RUNINFO_KEYS)
    # Pandas BUG casts int64 to float64,
    # https://github.com/pandas-dev/pandas/issues/9958
    for phs_key in PHS_RUNINFO_KEYS:
        series = new_known_runs[phs_key]
        is_nan = np.isnan(series.values)
        series.values[is_nan] = 0
        new_known_runs[phs_key] = series.astype(np.int32)
    return new_known_runs


def number_expected_phs_events(runinfo):
    count = np.zeros(runinfo.shape[0], dtype=np.int64)
    for key in TRIGGER_NUMBER_RUNINFO_KEYS:
        count += np.int64(np.round(runinfo[key]))
    count[np.isnan(count)] = 0.0
    return (np.round(count)).astype(np.int64)