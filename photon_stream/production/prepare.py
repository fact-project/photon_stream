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
from functools import lru_cache
from glob import glob

from .isdc._produce import QSUB_OBS_PRODUCE_PREFIX
from .runinfo import OBSERVATION_RUN_TYPE_KEY
from .runinfo import DRS_RUN_TYPE_KEY
from .runinfo import DRS_STEP_KEY
from . import tools


def jobs_and_directory_tree(
    runstatus,
    phs_dir='/gpfs0/fact/processing/public/phs',
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

    runstatus           A pandas DataFrame() of the FACT run-info-database which
                        is used as a reference for the runs to be processed.
                        All observation runs are taken into account. If you want
                        to process specific runs, remove the other runs from
                        runstatus.

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
    p['phs_introduction_path'] = join(p['phs_dir'], 'phs_introduction.pdf')

    fraction = np.random.uniform(size=runstatus.shape[0]) < only_a_fraction

    jobs = []
    for i, r in runstatus[fraction].iterrows():
        night = int(np.round(r.fNight))
        runid = int(np.round(r.fRunID))
        job = {}
        job['name'] = fact.path.template_to_path(night, runid, QSUB_OBS_PRODUCE_PREFIX+'_{N}_{R}')
        job['--raw_path'] = tree_path(
            night, runid, prefix=fact_raw_dir, suffix='.fits.fz'
        )
        if not exists(job['--raw_path']):
            print(night, runid, 'raw path', job['--raw_path'], 'does not exist.')
            continue

        if np.isnan(r.DrsRunID):
            print(night, runid, 'no drs run assigned.')
            continue
        else:
            drs_runid = int(np.round(r.DrsRunID))
        job['--drs_path'] = tree_path(
            night, drs_runid , prefix=fact_drs_dir, suffix='.drs.fits.gz'
        )
        if not exists(job['--drs_path']):
            print(night, runid, 'drs path', job['--drs_path'], 'does not exist.')
            continue

        aux_dir = dirname(tree_path(night, runid, prefix=fact_aux_dir, suffix=''))
        if not is_aux_dir_pointing_complete(aux_dir):
            print(night, runid, 'aux dir', aux_dir, 'is not complete yet.')
            continue

        job['--aux_dir'] = aux_dir
        job['--out_basename'] = fact.path.template_to_path(night, runid,'{N}_{R}')
        job['--out_dir'] = dirname(tree_path(night, runid, prefix=p['obs_dir'], suffix=''))
        job['--tmp_dir_basename'] = QSUB_OBS_PRODUCE_PREFIX
        job['--java_path'] = java_path
        job['--fact_tools_jar_path'] = fact_tools_jar_path
        job['--fact_tools_xml_path'] = fact_tools_xml_path
        job['o_path'] = tree_path(night, runid, prefix=p['std_dir'], suffix='.o')
        job['e_path'] = tree_path(night, runid, prefix=p['std_dir'], suffix='.e')
        jobs.append(job)

    return jobs, p


def output_tree(tree):
    os.makedirs(tree['phs_dir'], exist_ok=True, mode=0o755)
    readme_input_path = pkg_resources.resource_filename(
        'photon_stream',
        join('production','resources','phs_readme.md')
    )
    shutil.copy(readme_input_path, tree['phs_readme_path'])

    introduction_input_path = pkg_resources.resource_filename(
        'photon_stream',
        join('production','resources','phs_introduction.pdf')
    )
    shutil.copy(introduction_input_path, tree['phs_introduction_path'])
    os.makedirs(tree['obs_dir'], exist_ok=True, mode=0o755)
    os.makedirs(tree['std_dir'], exist_ok=True, mode=0o755)


@lru_cache(maxsize=128)
def is_aux_dir_pointing_complete(aux_dir):
    if not exists(aux_dir):
        return False
    ok = np.zeros(len(tools.DRIVE_AUX_FILE_KEYS), dtype=np.bool)
    for aux_file in glob(join(aux_dir,'*')):
        for i, aux_drive_key in enumerate(tools.DRIVE_AUX_FILE_KEYS):
            if aux_drive_key in aux_file: ok[i] = 1
    return np.all(ok)
