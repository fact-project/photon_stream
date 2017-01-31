import os
import numpy as np
import json
import subprocess
import datetime as dt

def jobs_where_path_exists(jobs, path='raw_path'):
    accesible_jobs = []
    for job in jobs:
        if os.path.exists(job[path]):
            accesible_jobs.append(job)
    return accesible_jobs


def night_id_2_yyyy(night):
    return night // 10000


def night_id_2_mm(night):
    return (night // 100) % 100


def night_id_2_nn(night):
    return night % 100


def number_of_events_in_run(run_path):
    ps = subprocess.Popen(['zcat', run_path], stdout=subprocess.PIPE)
    wc_out = subprocess.check_output(('wc', '-l'), stdin=ps.stdout)
    ps.wait()
    return int(wc_out)


def sparse_nights_in_range(start_nigth=20110101, end_nigth=20170301, gap_nights=27):
    current_night = dt.datetime.strptime(str(start_nigth), '%Y%m%d')
    nights = []
    while True:
        current_night += dt.timedelta(gap_nights)
        night = int(current_night.strftime(format='%Y%m%d'))
        if night > end_nigth:
            break
        print(night)
        nights.append(night)
    return nights
        