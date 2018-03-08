import os
import numpy as np
from os.path import join
from os.path import split
from os.path import exists
import glob
from tqdm import tqdm
import subprocess as sp
from .write_worker_node_script import write_worker_node_script

fact_queues = ['fact_long', 'fact_medium', 'fact_short']


def qsub(
    input_phs_dir,
    out_muon_dir,
):
    """
    Run the Muon extraction on all photon-stream runs in the 'phs' directory.
    """
    input_phs_dir = os.path.abspath(input_phs_dir)
    out_muon_dir = os.path.abspath(out_muon_dir)
    os.makedirs(out_muon_dir, exist_ok=True, mode=0o755)

    print('Start extracting muons...')

    run_paths = glob.glob(join(input_phs_dir, '*/*/*/*.phs.jsonl.gz'))

    print('Found', len(run_paths), 'potential runs.')
    print('Set up output paths for the potential runs...')

    potential_jobs = []
    for run_path in tqdm(run_paths):

        run_path = os.path.abspath(run_path)
        year = split(split(split(split(run_path)[0])[0])[0])[1]
        month = split(split(split(run_path)[0])[0])[1]
        night = split(split(run_path)[0])[1]
        base = split(run_path)[1].split('.')[0]
        job = {
            'input_run_path': run_path,
            'year': year,
            'month': month,
            'night': night,
            'base': base,
            'output_muon_path': join(
                out_muon_dir,
                'muons',
                year,
                month,
                night,
                base
            )
        }
        potential_jobs.append(job)

    print('Set up paths for', len(potential_jobs), 'potential runs.')
    print('Sort out all potential runs which were already processed...')

    jobs = []
    # check if output already exists
    for job in tqdm(potential_jobs):
        existing_path = glob.glob(job['output_muon_path']+'*')
        if len(existing_path) == 0:
            jobs.append(job)

    print('There are', len(jobs), 'runs left to be processed.')
    print('Submitt into qsub...')

    for job in tqdm(jobs):

        job['job_path'] = join(
            out_muon_dir,
            'job',
            job['year'],
            job['month'],
            job['night'],
            'fact_phs_muon_'+job['base']+'.sh')

        job['stdout_path'] = join(
            out_muon_dir,
            'std',
            job['year'],
            job['month'],
            job['night'],
            job['base']+'.o')

        job['stderr_path'] = join(
            out_muon_dir,
            'std',
            job['year'],
            job['month'],
            job['night'],
            job['base']+'.e')

        job_dir = os.path.split(job['job_path'])[0]
        os.makedirs(job_dir, exist_ok=True, mode=0o755)

        std_dir = os.path.split(job['stdout_path'])[0]
        os.makedirs(std_dir, exist_ok=True, mode=0o755)

        output_muon_dir = os.path.split(job['output_muon_path'])[0]
        os.makedirs(output_muon_dir, exist_ok=True, mode=0o755)

        write_worker_node_script(
            path=job['job_path'],
            input_run_path=job['input_run_path'],
            output_muon_path=job['output_muon_path'])

        cmd = [ 'qsub',
                '-q', fact_queues[np.random.randint(3)],
                '-o', job['stdout_path'],
                '-e', job['stderr_path'],
                job['job_path']]

        qsub_return_code = sp.call(cmd)
