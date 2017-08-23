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
    """
    Returns the number of lines inside a gzipped text file.
    """
    ps = subprocess.Popen(['zcat', run_path], stdout=subprocess.PIPE)
    wc_out = subprocess.check_output(('wc', '-l'), stdin=ps.stdout)
    ps.wait()
    return int(wc_out)