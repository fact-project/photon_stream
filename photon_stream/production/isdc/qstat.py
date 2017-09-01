"""
Call qstat to find jobs of the photon-stream processing
"""
import subprocess as sp
import pandas as pd
import xml.etree.ElementTree as XmlEt
import re


def qstat(marker='phs_obs'):
    xml = qstat_xml()
    jobs = jobs_in_qstatxml(xml)
    return jobs_2_run_ids(all_jobs=jobs, marker=marker)


def qstat_xml():
    """
    Returns a qstat xml string
    """
    try:
        out = sp.check_output(['qstat', '-xml'], stderr=sp.STDOUT)
    except sp.CalledProcessError as e:
        print('returncode', e.returncode)
        print('output', e.output)
    return out


def jobs_in_qstatxml(qstatxml):
    """
    Takes qstat xml string and returns a list of dicts of 
    qsub job name and qsub job state 
    """
    jobs = []
    root = XmlEt.fromstring(qstatxml)
    queue_info = root.find('queue_info')
    for job_list in queue_info.iter('job_list'):
        jobs.append(
                {
                    'name':job_list.find('JB_name').text,
                    'state':job_list.find('state').text
                }
        )
    job_info = root.find('job_info')
    for job_list in job_info.iter('job_list'):
        jobs.append(
                {
                    'name':job_list.find('JB_name').text,
                    'state':job_list.find('state').text,
                }
        )
    return jobs


def job_name_2_obs_run_id(job_name, regex='\d+'):
    """
    Returns observation run ID (Night and Run). Expects the first digit in the
    job_name to be the fNight and the second digit to be the fRunID.
    """
    p = re.compile(regex)
    digits = p.findall(job_name)
    assert len(digits) >= 2
    return {'fNight': int(digits[0]), 'fRunID': int(digits[1])}


def jobs_2_run_ids(all_jobs, marker='phs_obs'):
    """
    Returns DataFrame with fNight, fRunID, and qsub state.
    The run ids are parsed from the qsub name. Only names which have the marker 
    in them are considered.
   
    Example
    -------
    qsub name: 'phs_obs_20170101_001' has the marker 'phs_obs' in it and 
    yields fNight=20170101, and fRunID = 1.
    """
    obs_runs = []
    for job in all_jobs:
        if marker in job['name']:
            run = job_name_2_obs_run_id(job['name'])
            run['state'] = job['state']
            obs_runs.append(run)

    if len(obs_runs) > 0:
        return pd.DataFrame(obs_runs)
    else:
        return pd.DataFrame(columns=['fNight','fRunID','state'])

