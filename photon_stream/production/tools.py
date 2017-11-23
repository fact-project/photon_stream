import os
from os.path import dirname
from os.path import join
import fact
from .runinfo import OBSERVATION_RUN_TYPE_KEY
from .runinfo import DRS_RUN_TYPE_KEY
from ..event_list_reader import EventListReader
from fact.path import tree_path
import numpy as np
import json


def touch(path):
    with open(path, 'a') as out:
        os.utime(path)


def number_of_events_in_file(path):
    reader = EventListReader(path)
    number_of_events = 0
    for event in reader:
        number_of_events += 1
    return number_of_events


DRIVE_AUX_FILE_KEYS = [
    'DRIVE_CONTROL_SOURCE_POSITION',
    'DRIVE_CONTROL_TRACKING_POSITION',
    'DRIVE_CONTROL_POINTING_POSITION',
]


def create_fake_fact_dir(path, runinfo):
    fact_raw = join(path, 'raw')
    fact_aux = join(path, 'aux')
    n = -1
    for index, row in runinfo.iterrows():
        night = int(np.round(runinfo['fNight'][index]))
        run = int(np.round(runinfo['fRunID'][index]))
        run_type = int(np.round(runinfo['fRunTypeKey'][index]))

        if n != night:
            n = night
            nightly_aux_dir = dirname(tree_path(night, run, prefix=fact_aux, suffix=''))
            os.makedirs(nightly_aux_dir, exist_ok=True, mode=0o755)
            for daux in DRIVE_AUX_FILE_KEYS:
                with open(join(nightly_aux_dir, str(night)+'_'+daux+'.fits'), 'w') as auxf:
                    auxf.write('I am a fake '+daux+'aux file.')

        if run_type == DRS_RUN_TYPE_KEY:
            drs_path = tree_path(night, run, prefix=fact_raw, suffix='.drs.fits.gz')
            os.makedirs(dirname(drs_path), exist_ok=True, mode=0o755)
            with open(drs_path, 'w') as drs_file:
                drs_file.write('I am a fake FACT drs file.')

        if run_type == OBSERVATION_RUN_TYPE_KEY:
            run_path = tree_path(night, run, prefix=fact_raw, suffix='.fits.fz')
            os.makedirs(dirname(run_path), exist_ok=True, mode=0o755)
            with open(run_path, 'w') as raw_file:
                dummy_run = {
                    'fNight': night,
                    'fRunID': run, 
                    'NumExpectedPhsEvents': np.random.randint(0,25000),
                }
                raw_file.write(json.dumps(dummy_run))

