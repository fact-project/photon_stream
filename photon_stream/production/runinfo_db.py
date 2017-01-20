import os
from fact import credentials
import pandas as pd

def get_home_path():
    return os.path.expanduser("~")


def get_config_dir():
    return os.path.join(get_home_path(), '.photon_stream')


def get_runinfo_path():
    return os.path.join(get_config_dir_path(), 'runinfo.h5')


def get_fresh_runinfo_db():

    if not os.path.isdir(get_config_dir()):
        os.mkdir(get_config_dir())

    factdb = credentials.create_factdb_engine()
    print("Reading fresh RunInfo table, takes about 1min.")
    runinfo = pd.read_sql_table("RunInfo", factdb)
    with pd.HDFStore(get_runinfo_path()) as store:
        store.put("runinfo", runinfo)
    return runinfo


def get_runinfo_db():
    if os.path.exists(get_runinfo_path()):
        with pd.HDFStore(get_runinfo_path()) as store:
            return store["runinfo"]
    else:
    	return get_fresh_runinfo_db()
