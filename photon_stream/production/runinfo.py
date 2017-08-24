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

TRIGGER_NUMBER_RUNINFO_KEYS = [
    'fRunTypeKey',
    'fNumExt1Trigger',
    'fNumExt2Trigger',
    'fNumPhysicsTrigger',
    'fNumPedestalTrigger',
]

PHS_RUNINFO_KEYS = [
    'photon_stream_NumTrigger',
]


def download_latest_runinfo():
    factdb = credentials.create_factdb_engine()
    print("Reading fresh RunInfo table, takes about 1min.")
    return pd.read_sql_table(
        table_name="RunInfo",
        con=factdb,
        columns=ID_RUNINFO_KEYS + TRIGGER_NUMBER_RUNINFO_KEYS
    )

def read_runinfo_from_file(path='runinfo.msg'):
    return pd.read_msgpack(path)

def write_runinfo_to_file(runinfo, path='runinfo.msg'):
    runinfo.to_msgpack(path)


def create_fake_fact_dir(path, runinfo):
    for index, row in runinfo.iterrows():
        night_id = runinfo['fNight'][index]
        run_id = runinfo['fRunID'][index]
        run_type_key = runinfo['fRunTypeKey'][index]

        yyyy = '{yyyy:04d}'.format(yyyy=tools.night_id_2_yyyy(night_id))
        mm = '{mm:02d}'.format(mm=tools.night_id_2_mm(night_id))
        nn = '{nn:02d}'.format(nn=tools.night_id_2_nn(night_id))
        os.makedirs(os.path.join(path, 'raw', yyyy, mm, nn), exist_ok=True)
        
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