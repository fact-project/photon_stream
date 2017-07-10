import os
from os.path import abspath
from os.path import join
from os.path import exists
import shutil
import datetime as dt

from .runinfo import get_runinfo
from . import tools
from .runinfo import observation_runs_in_runinfo_in_night_range
from .runinfo import add_drs_run_info_to_jobs


def make_job_list(
    out_dir,
    start_night=20110101,
    end_night=20501231,
    only_a_fraction=1.0,
    fact_raw_dir='/fact/raw',
    fact_drs_dir='/fact/raw',
    fact_aux_dir='/fact/aux',
    java_path='/home/guest/relleums/java8/jdk1.8.0_111',
    fact_tools_jar_path='/home/guest/relleums/fact_photon_stream/fact-tools/target/fact-tools-0.18.0.jar',
    fact_tools_xml_path='/home/guest/relleums/fact_photon_stream/photon_stream/photon_stream/production/observations_pass4.xml',
    tmp_dir_base_name='fact_photon_stream_JOB_ID_',
    runinfo=None,
    only_append=True,
):
    """
    Returns a list of job dicts which contain all relevant paths to convert a
    raw FACT run into the photon-stream representation.

    Parameters
    ----------

    out_dir             The path to the output directory where the photon-stream
                        is collected. The out_dir is created if not existing.
    
    start_night         The start night integer 'YYYYmmnn', processes only runs 
                        after this night. (default 20110101)

    end_night           The end night integer 'YYYYmmnn', process only runs
                        until this night. (default 20501231)

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

    runinfo             A pandas DataFrame() of the FACT run-info-database which
                        is used as a reference for the runs to be processed.
                        (default None, download the latest run-info on the fly)

    only_append         If True, no output directories are created, but it is 
                        asserted that there already output directories.
    """
    
    print('Start photon stream conversion ...')

    out_dir = os.path.abspath(out_dir)
    fact_raw_dir = abspath(fact_raw_dir)
    fact_drs_dir = abspath(fact_drs_dir)
    fact_aux_dir = abspath(fact_aux_dir)
    
    res_dir = join(out_dir, 'resources')
    this_processing_resource_dir = join(
        res_dir, 
        dt.datetime.utcnow().strftime('%Y%m%d_%Hh%Mm%Ss_%fus_UTC')
    )
    std_dir = join(out_dir, 'std')
    job_dir = join(out_dir, 'job')
    phs_dir = join(out_dir, 'phs')

    if only_append:
        assert exists(out_dir)
        assert exists(std_dir)
        assert exists(job_dir)
        assert exists(phs_dir)
        assert exists(res_dir)
    else:
        os.makedirs(out_dir, exist_ok=True)
        os.makedirs(std_dir, exist_ok=True)
        os.makedirs(job_dir, exist_ok=True)
        os.makedirs(phs_dir, exist_ok=True)
        os.makedirs(res_dir, exist_ok=True)
        
    os.makedirs(this_processing_resource_dir, exist_ok=False)

    print('Copy resources ...')
    fact_tools_jar_path = os.path.abspath(
        shutil.copy(fact_tools_jar_path, this_processing_resource_dir)
    )
    fact_tools_xml_path = os.path.abspath(
        shutil.copy(fact_tools_xml_path, this_processing_resource_dir)
    )

    if runinfo is None:
        runinfo = get_runinfo()

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
        job['base_name'] = '{bsn:08d}_{rrr:03d}'.format(
            bsn=job['Night'],
            rrr=job['Run']
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

    jobs = tools.jobs_where_path_exists(jobs, path='raw_path')

    print('Found '+str(len(jobs))+' runs both in database and accesible in "'+fact_raw_dir+'".')
    print('Find matching drs calibration runs ...')

    jobs = add_drs_run_info_to_jobs(runinfo=runinfo, jobs=jobs)
    jobs = tools.jobs_where_path_exists(jobs=jobs, path='drs_path')

    print('Found '+str(len(jobs))+' with accesible drs files.')

    for job in jobs: 
        job['std_dir'] = std_dir
        job['std_yyyy_mm_nn_dir'] = join(job['std_dir'], job['yyyymmnn_dir'])
        job['std_out_path'] = join(job['std_yyyy_mm_nn_dir'], job['base_name']+'.o')
        job['std_err_path'] = join(job['std_yyyy_mm_nn_dir'], job['base_name']+'.e')

        job['job_dir'] = job_dir
        job['job_yyyy_mm_nn_dir'] = join(job['job_dir'], job['yyyymmnn_dir'])    
        job['job_path'] = join(job['job_yyyy_mm_nn_dir'], job['base_name']+'.sh')
        job['worker_tmp_dir_base_name'] = tmp_dir_base_name

        job['java_path'] = java_path
        job['fact_tools_jar_path'] = fact_tools_jar_path
        job['fact_tools_xml_path'] = fact_tools_xml_path

        job['phs_dir'] = phs_dir
        job['phs_yyyy_mm_nn_dir'] = join(job['phs_dir'], job['yyyymmnn_dir'])
    print('Done.')
    return jobs