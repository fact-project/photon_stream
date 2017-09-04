import os
from os.path import abspath
from os.path import join
from os.path import exists
from os.path import dirname
import shutil
import numpy as np
import pkg_resources
import fact
from fact.path import tree_path

from .runinfo import OBSERVATION_RUN_TYPE_KEY
from .runinfo import DRS_RUN_TYPE_KEY
from .runinfo import DRS_STEP_KEY
from . import tools


def jobs_and_directory_tree(
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
    
    print('Make jobs and directory tree ...')

    phs_dir = abspath(phs_dir)
    fact_raw_dir = abspath(fact_raw_dir)
    fact_drs_dir = abspath(fact_drs_dir)
    fact_aux_dir = abspath(fact_aux_dir)
    java_path = abspath(java_path)
    fact_tools_jar_path = abspath(fact_tools_jar_path)
    fact_tools_xml_path = abspath(fact_tools_xml_path)

    p = {'phs_dir': phs_dir}
    p['obs_dir'] = join(p['phs_dir'], 'obs')
    p['std_dir'] = join(p['phs_dir'], 'obs.std')

    p['fact_tools_jar_path'] = fact_tools_jar_path
    p['fact_tools_xml_path'] = fact_tools_xml_path

    p['phs_readme_path'] = join(p['phs_dir'], 'README.md')

    print('Find runs in night range '+str(start_night)+' to '+str(end_night)+' in runstatus.csv ...')
    
    ri = runinfo
    past_start = (ri['fNight'] >= start_night).values
    before_end = (ri['fNight'] < end_night).values
    fraction = np.random.uniform(size=ri.shape[0]) < only_a_fraction
    valid = past_start*before_end*fraction

    print('Found '+str(valid.sum())+' runs in runstatus.csv.')
    print('Find overlap with runs accessible in "'+fact_raw_dir+'" ...')

    jobs = []
    for i, r in ri[valid].iterrows():
        night = int(np.round(r.fNight))
        runid = int(np.round(r.fRunID))
        job = {}
        job['name'] = fact.path.template_to_path(night, runid, 'phs_obs_{N}_{R}')
        job['--raw_path'] = tree_path(
            night, runid, prefix=fact_raw_dir, suffix='.fits.fz'
        )
        if not exists(job['--raw_path']):
            print('not find obs: ', job['--raw_path'])
            continue

        if np.isnan(r.DrsRunID):
            continue
        else:
            drs_runid = int(np.round(r.DrsRunID))
        job['--drs_path'] = tree_path(
            night, drs_runid , prefix=fact_drs_dir, suffix='.drs.fits.gz'
        )
        if not exists(job['--drs_path']):
            print('not find drs: ', job['--drs_path'])
            continue

        job['--aux_dir'] = dirname(tree_path(night, runid, prefix=fact_aux_dir, suffix=''))
        job['--out_basename'] = fact.path.template_to_path(night, runid,'{N}_{R}')
        job['--out_dir'] = dirname(tree_path(night, runid, prefix=p['obs_dir'], suffix=''))
        job['--tmp_dir_basename'] = 'phs_obs_'
        job['--java_path'] = java_path
        job['--fact_tools_jar_path'] = fact_tools_jar_path
        job['--fact_tools_xml_path'] = fact_tools_xml_path
        job['o_path'] = tree_path(night, runid, prefix=p['std_dir'], suffix='.o')
        job['e_path'] = tree_path(night, runid, prefix=p['std_dir'], suffix='.e')
        jobs.append(job)
        
    print('Found '+str(len(jobs))+' runs both in runstatus.csv and accesible in "'+fact_raw_dir+'".')
    return jobs, p


def output_tree(tree):
    os.makedirs(tree['phs_dir'], exist_ok=True, mode=0o755)
    readme_input_path = pkg_resources.resource_filename(
        'photon_stream', 
        join('production','resources','phs_readme.md')
    ) 
    shutil.copy(readme_input_path, tree['phs_readme_path'])
    os.makedirs(tree['obs_dir'], exist_ok=True, mode=0o755)
    os.makedirs(tree['std_dir'], exist_ok=True, mode=0o755)