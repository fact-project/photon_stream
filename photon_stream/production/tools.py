import os
import numpy as np
import json
import subprocess

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

def write_json(path, dic):
    with open(path, 'w') as job_out:
        job_out.write(json.dumps(un_numpyify_dictionary(dic), indent=4))

def un_numpyify_dictionary(dic):
    ret = {}
    for k, v in list(dic.items()):
        if isinstance(v, dict):
            ret[k] = un_numpyify_dictionary(v)
        elif isinstance(v, np.ndarray):
            if v.dtype == np.float32:
                v = v.astype(np.float64)
            ret[k] = v.tolist()
        elif isinstance(v, np.floating):
            ret[k] = float(v)
        elif isinstance(v, np.integer):
            ret[k] = int(v)
        else:
            ret[k] = v
    return ret

def number_of_events_in_run(run_path):
    ps = subprocess.Popen(['zcat', run_path], stdout=subprocess.PIPE)
    wc_out = subprocess.check_output(('wc', '-l'), stdin=ps.stdout)
    ps.wait()
    return int(wc_out)