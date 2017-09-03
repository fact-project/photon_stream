import pandas as pd
import re
import qstat as qstat2dict


def qstat(is_in_JB_name='phs_obs', xml=None):
    """
    Returns DataFrame(columns=['fNight','fRunID']) of all jobs in qstat
    which contain 'name' in their qstat JB_name. fNight and fRunID are parsed 
    from the JB_name which is for the photon-stream:

    JB_name: phs_{key:%s}_{yyyymmnn:08d}_{rrr:03d}

    key can be e.g. 'obs' for raw observation run processing

    yyyymmnn is fNight

    RRR is the fRunID
    """
    if xml is None:
        q_jobs = qstat2dict.qstat()
    else:
        q_jobs = qstat2dict._tools.xml2job_infos(xml)
    return q_jobs_2_runqstat(q_jobs, is_in_JB_name)


def JB_name_2_run_ids(JB_name, regex='\d+'):
    """
    Returns observation run ID (Night and Run). Expects the first digit in the
    JB_name to be the fNight and the second digit to be the fRunID.
    """
    p = re.compile(regex)
    digits = p.findall(JB_name)
    assert len(digits) >= 2
    return {'fNight': int(digits[0]), 'fRunID': int(digits[1])}


def q_jobs_2_runqstat(q_jobs, is_in_JB_name):
    jobs = []
    for q_job in q_jobs:
        if is_in_JB_name in q_job['JB_name']:
            jobs.append(JB_name_2_run_ids(q_job['JB_name']))
    if len(jobs) > 0:
        return pd.DataFrame(jobs)
    else:
        return pd.DataFrame(columns=['fNight','fRunID'])