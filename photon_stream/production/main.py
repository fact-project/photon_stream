"""
Facttools job submitter for ISDC

Usage:
  submit.py [options] 
Options:
  -h --help          Show this screen.
  --version          Show version.
  -i --infiles STR   what files should be analysed. [default: /fact/raw/2016/01/01/20160101_0[01]*.fits.fz]
  -p --print         just print the commands, instead of submitting
"""

import sys
from docopt import docopt
import glob
import os
from tqdm import tqdm
import subprocess as sp
import numpy as np
import json

from .submit_qsub_job import submit_qsub_job
from .runinfo import get_runinfo
from .tools import mkdirs
from .tools import jobs_where_path_exists
from .write_worker_script import write_worker_script


def submit_single_pulse_conversion_to_qsub(
    out_dir, 
    start_nigth=20110101, 
    end_nigth=20501231,
    fact_dir='/fact/', 
    java_path='/usr/java/jdk1.8.0_77/bin'
    fact_tools_jar_path='/fac_tools.jar',
    fact_tools_xml_path='/observations_pass3.xml',
    tmp_dir_base_name='fact_photon_stream_JOB_ID_',
    queue='fact_medium', 
    email='sebmuell@phys.ethz.ch',
    print_only=True):
    
    std_dir = os.path.join(out_dir, 'std')
    job_dir = os.path.join(out_dir, 'job')

    mkdirs(dir=out_dir)
    mkdirs(dir=std_dir)
    mkdirs(dir=job_dir)

    runinfo = get_runinfo()

    print('Find runs in night range '+str(start_nigth)+' to '+str(end_nigth)+' in runinfo database ...')
    
    jobs = observation_runs_in_runinfo_in_night_range(
        runinfo=runinfo,
        start_nigth=start_nigth, 
        end_nigth=end_nigth)

    print('Found '+str(len(jobs))+' runs in database.')
    print('Find intersection with runs accessible in "'+raw_dir+'" ...')

    jobs = add_run_path_info(fact_dir=fact_dir, runs=jobs)
    jobs = jobs_where_path_exists(jobs, path='raw_path')

    print('Found '+str(len(jobs))+' runs both in database and accesible in "'+raw_dir+'".')
    print('Find matching drs calibration runs ...')

    jobs = add_drs_run_info_to_jobs(runinfo=runinfo, jobs=jobs)
    jobs = runs_accesible(jobs=jobs, key='drs_path')

    print('Found '+str(len(jobs))+' with accesible drs files.')

    for job in tqdm(jobs): 
        job['std_dir'] = std_dir
        job['stdout_path'] = os.path.join(std_dir, job['base_name']+'.o')
        job['stderr_path'] = os.path.join(std_dir, job['base_name']+'.e')
        job['job_dir'] = job_dir
        job['job_path'] = os.path.join(job_dir, job['base_name']+'_job.json')
        
        job['worker_script_path'] = os.path.join(job_dir, job['base_name']+'_PhotonStram'+'.sh')
        job['worker_tmp_dir_base_name'] = tmp_dir_base_name
        job['email'] = email
        job['queue'] = queue

        job['java_path'] = java_path
        job['fact_tools_jar_path'] = fact_tools_jar_path,
        job['fact_tools_xml_path'] = fact_tools_xml_path,

        job['out_dir'] = os.path.join(out_dir, job['yyyymmdd_dir'])

        write_worker_script(
            path=job['worker_script_path'],
            in_run_path=job['raw_path'],
            drs_path=job['drs_path'],
            aux_dir=job['aux_dir'],
            out_dir=job['out_dir'],
            out_base_name=job['base_name'],
            java_path=job['java_path'],
        )

        cmd = [ 'qsub ',
                '-q', queu,
                '-o', job['stdout_path'],
                '-e', job['stderr_path'],
                '-m', 'ae', # send email in case of (e)nd or (a)bort
                '-M', email,
                job['worker_script_path']]
   
        if print_only:
            print(cmd)
            job['qsub_return_code'] = 0
        else:
            job['qsub_return_code'] = sp.check_output(cmd)

        with open(job['job_path'], 'w') as job_out:
            job_out.write(json.dumps(job, indent=4))