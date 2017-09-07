from tqdm import tqdm
import os
from os.path import join
import numpy as np
from shutil import which
from .. import prepare
from .. import runstatus as rs
from .. import runinfo as ri
from .qsub import qsub
from .qsub import QUEUE_NAME

QSUB_OBS_PRODUCE_PREFIX = 'phs_obs_'


def produce(
    only_a_fraction=1.0,
    fact_raw_dir='/fact/raw',
    fact_drs_dir='/fact/raw',
    fact_aux_dir='/fact/aux',
    phs_dir='/gpfs0/fact/processing/public/phs',
    java_path='/home/guest/relleums/java8/jdk1.8.0_111',
    fact_tools_jar_path='/home/guest/relleums/fact_photon_stream/fact-tools/target/fact-tools-0.18.1.jar',
    fact_tools_xml_path='/home/guest/relleums/fact_photon_stream/photon_stream/photon_stream/production/resources/observations_pass4.xml',
    tmp_dir_base_name='phs_obs_',
    queue=QUEUE_NAME,
    max_jobs_in_qsub=256,
    runs_in_qstat=None,
):  
    obs_dir = join(phs_dir, 'obs')
    runstatus_path = join(obs_dir, 'runstatus.csv')
    runstatus = rs.read(runstatus_path)

    all_runjobs = runstatus[np.isnan(runstatus['PhsSize'])]

    if runs_in_qstat is None:
        runs_in_qstat = ps.production.isdc.qstat.qstat(is_in_JB_name=QSUB_OBS_PRODUCE_PREFIX)

    if len(runs_in_qstat) > max_jobs_in_qsub:
        return

    runjobs = ri.remove_from_first_when_also_in_second(
        first=all_runjobs,
        second=runs_in_qstat,
    )

    num_runs_for_qsub = max_jobs_in_qsub - len(runs_in_qstat)

    runjobs.sort_values(by=ri.ID_RUNINFO_KEYS , inplace=True, ascending=False)

    jobs, tree = prepare.jobs_and_directory_tree(
        phs_dir=phs_dir,
        only_a_fraction=only_a_fraction,
        fact_raw_dir=fact_raw_dir,
        fact_drs_dir=fact_drs_dir,
        fact_aux_dir=fact_aux_dir,
        java_path=java_path,
        fact_tools_jar_path=fact_tools_jar_path,
        fact_tools_xml_path=fact_tools_xml_path,
        tmp_dir_base_name=tmp_dir_base_name,
        runstatus=runjobs,
    )
    prepare.output_tree(tree)

    i = 0
    for job in tqdm(jobs, desc='qsub'):
        if i > num_runs_for_qsub:
            break
        i += 1
        qsub(
            job=job, 
            exe_path=which('phs.isdc.obs.produce.worker'),
            queue=queue,
        )