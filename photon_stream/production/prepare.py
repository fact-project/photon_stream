import os
from os.path import abspath
from os.path import join
from os.path import exists
import shutil
import numpy as np
import pkg_resources

from .runinfo import OBSERVATION_RUN_TYPE_KEY
from .runinfo import DRS_RUN_TYPE_KEY
from . import tools
 

def make_job_list(
    runinfo,
    phs_dir='/gpfs0/fact/processing/public/phs',
    start_night=0,
    end_night=99999999,
    only_a_fraction=1.0,
    fact_raw_dir='/fact/raw',
    fact_drs_dir='/fact/raw',
    fact_aux_dir='/fact/aux',
    java_path='/home/guest/relleums/java8/jdk1.8.0_111',
    fact_tools_jar_path='/home/guest/relleums/fact_photon_stream/fact-tools/target/fact-tools-0.18.0.jar',
    fact_tools_xml_path='/home/guest/relleums/fact_photon_stream/photon_stream/photon_stream/production/resources/observations_pass4.xml',
    tmp_dir_base_name='phs_obs_',
):
    """
    Returns a list of job dicts which contain all relevant p to convert a
    raw FACT run into the photon-stream representation.

    Parameters
    ----------

    phs_dir             Output directory of the photon-stream. In there is the
                        observations directory ./obs and simulations directory
                        ./sim
    
    runinfo             A pandas DataFrame() of the FACT run-info-database which
                        is used as a reference for the runs to be processed.
                        All observation runs are taken into account. If you want
                        to process specific runs, remove the other runs from
                        runinfo.

    start_night         The start night integer 'YYYYmmnn', processes only runs 
                        after this night. (default 0)

    end_night           The end night integer 'YYYYmmnn', process only runs
                        until this night. (default 99999999)

    only_a_fraction     A ratio between 0.0 and 1.0 to only process a 
                        random fraction of the runs. Usefull for debugging over 
                        long periodes of observations. (default 1.0)

    fact_raw_dir        The path to the FACT raw observation directory.

    fact_drs_dir        The path to the FACT drs calibration directory.

    fact_aux_dir        The path to the FACT auxiliary directory.

    java_path           The path to the JAVA run time environment to be used for
                        fact-tools.

    fact_tools_jar_path The path to the fact-tools java-jar executable file.

    fact_tools_xml_path The path to the fact-tools steering xml file.

    tmp_dir_base_name   The base name of the temporary directory on the qsub 
                        worker nodes. (default 'fact_photon_stream_JOB_ID_')
    """
    
    print('Make raw->phs job list ...')

    phs_dir = abspath(phs_dir)
    fact_raw_dir = abspath(fact_raw_dir)
    fact_drs_dir = abspath(fact_drs_dir)
    fact_aux_dir = abspath(fact_aux_dir)
    java_path = abspath(java_path)
    fact_tools_jar_path = abspath(fact_tools_jar_path)
    fact_tools_xml_path = abspath(fact_tools_xml_path)

    p = {'phs_dir': phs_dir}
    p['obs_dir'] = join(p['phs_dir'], 'obs')
    p['std_dir'] = join(p['phs_dir'], '.obs.std')
    p['job_dir'] = join(p['phs_dir'], '.obs.job')

    p['fact_tools_jar_path'] = fact_tools_jar_path
    p['fact_tools_xml_path'] = fact_tools_xml_path

    p['phs_readme_path'] = join(p['phs_dir'], 'README.md')

    print('Find runs in night range '+str(start_night)+' to '+str(end_night)+' in runinfo database ...')
    
    jobs = observation_runs_in_runinfo_in_night_range(
        runinfo=runinfo,
        start_night=start_night, 
        end_night=end_night,
        only_a_fraction=only_a_fraction
    )

    print('Found '+str(len(jobs))+' runs in database.')
    print('Find overlap with runs accessible in "'+fact_raw_dir+'" ...')

    for job in jobs:
        job['yyyy'] = tools.night_id_2_yyyy(job['Night'])
        job['mm'] = tools.night_id_2_mm(job['Night'])
        job['nn'] = tools.night_id_2_nn(job['Night'])
        job['fact_raw_dir'] = fact_raw_dir
        job['fact_drs_dir'] = fact_drs_dir
        job['fact_aux_dir'] = fact_aux_dir
        job['yyyymmnn_dir'] = '{y:04d}/{m:02d}/{n:02d}/'.format(
            y=job['yyyy'],
            m=job['mm'],
            n=job['nn']
        )
        job['base_name'] = '{Night:08d}_{Run:03d}'.format(
            Night=job['Night'],
            Run=job['Run']
        )
        job['raw_file_name'] = job['base_name']+'.fits.fz'
        job['raw_path'] = join(
            job['fact_raw_dir'], 
            job['yyyymmnn_dir'], 
            job['raw_file_name']
        )
        job['aux_dir'] = join(
            job['fact_aux_dir'], 
            job['yyyymmnn_dir']
        )

    jobs = jobs_where_path_exists(jobs, path='raw_path')

    print('Found '+str(len(jobs))+' runs both in database and accesible in "'+fact_raw_dir+'".')
    print('Find matching drs calibration runs ...')

    jobs = add_drs_run_info_to_jobs(runinfo=runinfo, jobs=jobs)
    jobs = jobs_where_path_exists(jobs, path='drs_path')

    print('Found '+str(len(jobs))+' with accesible drs files.')

    for job in jobs: 
        job['std_dir'] = p['std_dir']
        job['std_yyyy_mm_nn_dir'] = join(job['std_dir'], job['yyyymmnn_dir'])
        job['std_out_path'] = join(job['std_yyyy_mm_nn_dir'], job['base_name']+'.o')
        job['std_err_path'] = join(job['std_yyyy_mm_nn_dir'], job['base_name']+'.e')

        job['job_dir'] = p['job_dir']
        job['job_yyyy_mm_nn_dir'] = join(job['job_dir'], job['yyyymmnn_dir'])    
        job['job_path'] = join(job['job_yyyy_mm_nn_dir'], job['base_name']+'.sh')
        job['worker_tmp_dir_base_name'] = tmp_dir_base_name

        job['java_path'] = java_path
        job['fact_tools_jar_path'] = fact_tools_jar_path
        job['fact_tools_xml_path'] = fact_tools_xml_path

        job['obs_dir'] = p['obs_dir']
        job['obs_yyyy_mm_nn_dir'] = join(job['obs_dir'], job['yyyymmnn_dir'])
    print('Done.')

    return {
        'jobs': jobs,
        'tree': p
    }



def prepare_output_tree(tree):
    print('Prepare output directory tree ...')
    
    os.makedirs(tree['phs_dir'], exist_ok=True, mode=0o755)
    readme_input_path = pkg_resources.resource_filename(
        'photon_stream', 
        join('production','resources','phs_readme.md')
    ) 
    shutil.copy(readme_input_path, tree['phs_readme_path'])

    os.makedirs(tree['obs_dir'], exist_ok=True, mode=0o755)
    os.makedirs(tree['std_dir'], exist_ok=True, mode=0o755)
    os.makedirs(tree['job_dir'], exist_ok=True, mode=0o755)



def observation_runs_in_runinfo_in_night_range(
    runinfo, 
    start_night=0, 
    end_night=99999999,
    only_a_fraction=1.0
):
    past_start = (runinfo['fNight'] >= start_night).as_matrix()
    before_end = (runinfo['fNight'] < end_night).as_matrix()
    is_obs = (runinfo['fRunTypeKey'] == OBSERVATION_RUN_TYPE_KEY).as_matrix()
    valid = past_start*before_end*is_obs

    fraction = np.random.uniform(size=len(valid)) < only_a_fraction
    
    night_ids = runinfo['fNight'][valid*fraction]
    run_ids = runinfo['fRunID'][valid*fraction]

    jobs = []

    for i, run_id in enumerate(run_ids):
        jobs.append(
            {
                'Night': np.int(np.round(night_ids.iloc[i])),
                'Run': np.int(np.round(run_id))
            }
        )
    return jobs


def add_drs_run_info_to_jobs(runinfo, jobs):
    for job in jobs:   
        drs_run_candidates = runinfo[
            (runinfo.fNight == job["Night"])&
            (runinfo.fDrsStep == 2)&
            (runinfo.fRunTypeKey == 2)&
            (runinfo.fRunID < job["Run"])
        ]
        
        if len(drs_run_candidates) >= 1:
            job["drs_Run"] = drs_run_candidates.iloc[-1].fRunID
            job["drs_file_name"] = '{Night:08d}_{Run:03d}.drs.fits.gz'.format(
                Night=job['Night'],
                Run=int(job["drs_Run"])
            )
            job['drs_path'] = os.path.join(
                job['fact_drs_dir'], 
                job['yyyymmnn_dir'], 
                job['drs_file_name']
            )
        else:
            job["drs_Run"] = None
            job['drs_path'] = 'nope.sorry'
    return jobs


def jobs_where_path_exists(jobs, path='raw_path'):
    accesible_jobs = []
    for job in jobs:
        if os.path.exists(job[path]):
            accesible_jobs.append(job)
    return accesible_jobs