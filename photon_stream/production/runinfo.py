from fact import credentials
import pandas as pd
import shutil

OBSERVATION_RUN_TYPE_KEY = 1
DRS_RUN_TYPE_KEY = 2

DRS_STEP_KEY = 2

ID_RUNINFO_KEYS = [
    'fNight',
    'fRunID',
]

TRIGGER_NUMBER_RUNINFO_KEYS = [
    'fNumExt1Trigger',
    'fNumExt2Trigger',
    'fNumPhysicsTrigger',
    'fNumPedestalTrigger',
]

RUNINFO_KEYS = (
    ID_RUNINFO_KEYS +
    ['fRunTypeKey'] +
    ['fDrsStep'] +
    TRIGGER_NUMBER_RUNINFO_KEYS
)

PHS_STATUS_KEYS = [
    'NumActualPhsEvents',
    'PhsSize',
    'StdOutSize',
    'StdErrorSize',
]

PHS_KEYS = (
    ['NumExpectedPhsEvents'] +
    PHS_STATUS_KEYS +
    ['IsOk'] +
    ['StatusIteration']
)

RUNSTATUS_KEYS = (
    ID_RUNINFO_KEYS +
    ['DrsRunID'] +
    PHS_KEYS
)


def read(path='runinfo.csv'):
    return pd.read_csv(path, sep='\t')


def write(runinfo, path='runinfo.csv'):
    runinfo.to_csv(
        path+'.part', 
        index=False, 
        na_rep='nan', 
        float_format='%.0f',
        sep='\t'
    )
    shutil.move(path+'.part', path)


def download_latest():
    factdb = credentials.create_factdb_engine()
    return pd.read_sql_table(
        table_name="RunInfo",
        con=factdb,
        columns=RUNINFO_KEYS
    )


def remove_from_first_when_also_in_second(first, second):
    m = pd.merge(
        first,
        second, 
        how='outer', 
        indicator=True,
        on=ID_RUNINFO_KEYS,
    )
    result = m[m['_merge'] == 'left_only'].copy()
    result.drop('_merge', axis=1, inplace=True)
    return result