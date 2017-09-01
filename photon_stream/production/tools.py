import datetime as dt
import os
import numpy as np


def night_id_2_yyyy(night):
    return np.int(np.round(night)) // 10000


def night_id_2_mm(night):
    return (np.int(np.round(night)) // 100) % 100


def night_id_2_nn(night):
    return np.int(np.round(night)) % 100


def time_stamp_utcnow_for_valid_path():
	return dt.datetime.utcnow().strftime('%Y%m%d_%Hh%Mm%Ss_%fus_UTC')


def local_backup_path_with_timestamp(path):
    time_stamp = time_stamp_utcnow_for_valid_path()
    basename = os.path.basename(path)
    dirname = os.path.dirname(path)
    return os.path.join(dirname, '.'+basename+'.'+time_stamp)


def touch(path):
    with open(lock_path, 'a') as out:
        os.utime(lock_path)