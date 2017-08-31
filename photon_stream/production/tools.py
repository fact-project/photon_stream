import datetime as dt
import os


def night_id_2_yyyy(night):
    return night // 10000


def night_id_2_mm(night):
    return (night // 100) % 100


def night_id_2_nn(night):
    return night % 100


def time_stamp_utcnow_for_valid_path():
	return dt.datetime.utcnow().strftime('%Y%m%d_%Hh%Mm%Ss_%fus_UTC')


def local_backup_path_with_timestamp(path):
    time_stamp = time_stamp_utcnow_for_valid_path()
    basename = os.path.basename(path)
    dirname = os.path.dirname(path)
    return os.path.join(dirname, '.'+basename+'.'+time_stamp)