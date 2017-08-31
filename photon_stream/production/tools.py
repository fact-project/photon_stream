import datetime as dt


def night_id_2_yyyy(night):
    return night // 10000


def night_id_2_mm(night):
    return (night // 100) % 100


def night_id_2_nn(night):
    return night % 100


def time_stamp_utcnow_for_valid_path():
	return dt.datetime.utcnow().strftime('%Y%m%d_%Hh%Mm%Ss_%fus_UTC')