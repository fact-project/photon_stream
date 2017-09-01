#! /usr/bin/env python
"""
Converting FACT raw observation runs into photon-stream runs. You need to export
the universal FACT password: export FACT_PASSWORD=*********

Usage: phs.production.isdc.automatic [options]

Options:
    --fact_raw_dir=PATH         [default: /fact/raw]
    --fact_drs_dir=PATH         [default: /fact/raw]
    --fact_aux_dir=PATH         [default: /fact/aux]
    --fact_phs_dir=PATH         [default: /gpfs0/fact/processing/public/phs]
    --java_path=PATH            [default: /home/guest/relleums/java8/jdk1.8.0_111]
    --fact_tools_jar_path=PATH  [default: /home/guest/relleums/fact_photon_stream/fact-tools/target/fact-tools-0.18.0.jar']
    --fact_tools_xml_path=PATH  [default: /home/guest/relleums/fact_photon_stream/photon_stream/photon_stream/production/resources/observations_pass4.xml']
    --queue=NAME                [default: fact_medium]
    --start_night=NIGHT         [default: 00000000]
    --end_night=NIGHT           [default: 99999999]
    --use_dummy_qsub=FLAG       [default: False]
    --max_jobs_in_qsub=INT      [default: 128]
    --only_a_fraction=FLOAT     [default: 1.0]
    --start_new=FLAG            [default: False]
"""
import docopt
import filelock
from tqdm import tqdm
import os
from os.path import join
import subprocess as sp
from .dummy_qsub import dummy_qsub
from .. import prepare
from .write_worker_script import write_worker_script
from .. import runinfo
from .. import status
import pandas as pd

def qsub(
    
    start_night=0,
    end_night=99999999,
    only_a_fraction=1.0,
    fact_raw_dir='/fact/raw',
    fact_drs_dir='/fact/raw',
    fact_aux_dir='/fact/aux',
    phs_dir='/gpfs0/fact/processing/public/phs',
    java_path='/home/guest/relleums/java8/jdk1.8.0_111',
    fact_tools_jar_path='/home/guest/relleums/fact_photon_stream/fact-tools/target/fact-tools-0.18.0.jar',
    fact_tools_xml_path='/home/guest/relleums/fact_photon_stream/photon_stream/photon_stream/production/resources/observations_pass4.xml',
    tmp_dir_base_name='phs_obs_',
    queue='fact_medium', 
    use_dummy_qsub=False,
    qstat_dummy=None,
    job_runinfo=None,
    start_new=False,
    max_jobs_in_qsub=128,
):  
    lock_path = join(phs_dir,'obs','.lock')
    runstatus_path = join(phs_dir,'obs','runstatus.csv')

    if start_new:        
        obs_dir = join(phs_dir,'obs')
        if not os.path.exists(runstatus_path):
            os.makedirs(obs_dir, exist_ok=True, mode=0o777)
            if job_runinfo is None:
                job_runinfo = runinfo.download_latest()
            runinfo.write(job_runinfo, runstatus_path)
            status.status(
                obs_dir=obs_dir,
                runstatus_path=runstatus_path,
            )
        with open(lock_path, 'a') as out:
            os.utime(lock_path)



    lock = filelock.FileLock(lock_path)
    
    try:
        with lock.acquire(timeout=1):
            if job_runinfo is None:
                job_runinfo = runinfo.download_latest()

            runstatus = runinfo.read(runstatus_path)
            new_runstatus = runinfo.append_runinfo_to_runstatus(job_runinfo, runstatus)
            runinfo.write(new_runstatus, runstatus_path)
            runstatus = new_runstatus

            obs_runstatus = runstatus[runstatus['fRunTypeKey']==runinfo.OBSERVATION_RUN_TYPE_KEY]
            actual_phs = obs_runstatus['PhotonStreamNumEvents']
            expected_phs = runinfo.number_expected_phs_events(obs_runstatus)
            phs_deficit = expected_phs - actual_phs
            all_runjobs = obs_runstatus[phs_deficit > 0]

            if qstat_dummy is None:
                runqstat = ps.production.isdc.qstat.qstat(name='phs_obs')
            else:
                runqstat = qstat_dummy

            if len(runqstat) > max_jobs_in_qsub:
                print('Stop. Qsub is busy.')
                return

            runjobs = runinfo.obs_runs_not_in_qstat(
                all_runjobs=all_runjobs,
                runqstat=runqstat,
            )

            runinfo_todo = runinfo.remove_all_obs_runs_from_runinfo_not_in_runjobs(
                runinfo=job_runinfo,
                runjobs=runjobs,
            )

            todo = prepare.make_job_list(
                phs_dir=phs_dir,
                start_night=start_night,
                end_night=end_night,
                only_a_fraction=only_a_fraction,
                fact_raw_dir=fact_raw_dir,
                fact_drs_dir=fact_drs_dir,
                fact_aux_dir=fact_aux_dir,
                java_path=java_path,
                fact_tools_jar_path=fact_tools_jar_path,
                fact_tools_xml_path=fact_tools_xml_path,
                tmp_dir_base_name=tmp_dir_base_name,
                runinfo=runinfo_todo,
            )

            prepare.prepare_output_tree(todo['tree'])

            for job in tqdm(todo['jobs']):
                os.makedirs(job['job_yyyy_mm_nn_dir'], exist_ok=True, mode=0o777)
                os.makedirs(job['std_yyyy_mm_nn_dir'], exist_ok=True, mode=0o777)

                write_worker_script(
                    path=job['job_path'],
                    java_path=job['java_path'],
                    fact_tools_jar_path=job['fact_tools_jar_path'],
                    fact_tools_xml_path=job['fact_tools_xml_path'],
                    in_run_path=job['raw_path'],
                    drs_path=job['drs_path'],
                    aux_dir=job['aux_dir'],
                    out_dir=job['obs_yyyy_mm_nn_dir'],
                    out_base_name=job['base_name'],
                    tmp_dir_base_name=job['worker_tmp_dir_base_name'],
                )

                cmd = [ 
                    'qsub',
                    '-q', queue,
                    '-o', job['std_out_path'],
                    '-e', job['std_err_path'],
                    '-N', 
                    'phs_obs_{yyyymmnn:08d}_{rrr:03d}'.format(
                        yyyymmnn=job['Night'],
                        rrr=job['Run']
                    ),
                    job['job_path']
                ]
           
                if use_dummy_qsub:
                    dummy_qsub(cmd)
                else:
                    try:
                        sp.check_output(cmd, stderr=sp.STDOUT)
                    except sp.CalledProcessError as e:
                        print('returncode', e.returncode)
                        print('output', e.output)
                        raise

            print('Stop.')      
    except filelock.Timeout:
        print('Stop. Submission is locked.')


def main():
    try:
        arguments = docopt.docopt(__doc__)
        setup_logging(arguments['--logfile'], arguments['--verbose'])
        run(
            fact_password=arguments['--fact_password'],
            raw_dir=arguments['--raw_dir'], 
            phs_dir=arguments['--phs_dir'],
            runstatus_path=arguments['--runstatus_path'],
            max_jobs_in_qsub=int(arguments['--max_jobs_in_qsub']),
            qsub_history_path=arguments['--qsub_history_path'],
        )

    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()