from tqdm import tqdm
import os
from os.path import join
import numpy as np
import pkg_resources

from .. import prepare
from .. import runstatus as rs
from .. import runinfo as ri
from .qsub import qsub

worker_node_main_path = os.path.abspath(
    pkg_resources.resource_filename(
        'photon_stream', 
        os.path.join('production','isdc','worker_node_produce.py')
    )
)

def produce(
    start_night=0,
    end_night=99999999,
    only_a_fraction=1.0,
    fact_raw_dir='/fact/raw',
    fact_drs_dir='/fact/raw',
    fact_aux_dir='/fact/aux',
    phs_dir='/gpfs0/fact/processing/public/phs',
    java_path='/home/guest/relleums/java8/jdk1.8.0_111',
    fact_tools_jar_path='/home/guest/relleums/fact_photon_stream/fact-tools/target/fact-tools-0.18.1.jar',
    fact_tools_xml_path='/home/guest/relleums/fact_photon_stream/photon_stream/photon_stream/production/resources/observations_pass4.xml',
    tmp_dir_base_name='phs_obs_',
    queue='fact_medium', 
    latest_runstatus=None,
    max_jobs_in_qsub=256,
    use_dummy_qsub=False,
    runqstat_dummy=None,
):  
    print('Start fact/raw to public/phs/obs.')

    print('Update runstatus.csv from La Palma ...')
    obs_dir = join(phs_dir,'obs')
    rs.update_to_latest(
        obs_dir=obs_dir, 
        latest_runstatus=latest_runstatus
    )
    runstatus = rs.read(join(obs_dir, 'runstatus.csv'))
    print('Update runstatus.csv done.')

    needs_processing = np.isnan(runstatus['IsOk'].values)
    all_runjobs = runstatus[needs_processing]
    print(str(len(all_runjobs))+' runs need processing.')

    if runqstat_dummy is None:
        runqstat = ps.production.isdc.qstat.qstat(is_in_JB_name='phs_obs')
    else:
        runqstat = runqstat_dummy

    if len(runqstat) > max_jobs_in_qsub:
        print('Stop. Qsub is busy. '+str(len(runqstat))+' jobs in the queue.')
        return

    runjobs = ri.remove_from_first_when_also_in_second(
        first=all_runjobs,
        second=runqstat,
    )
    print(str(len(runjobs))+' runs need processing and are not yet in the queue.')
    
    num_runs_for_qsub = max_jobs_in_qsub - len(runqstat)
    print('Qsub is good to go for '+str(num_runs_for_qsub)+' of '+str(max_jobs_in_qsub)+' more jobs.')

    runjobs.sort_values(by=ri.ID_RUNINFO_KEYS , inplace=True, ascending=False)

    jobs, tree = prepare.jobs_and_directory_tree(
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
        runinfo=runjobs,
    )
    prepare.output_tree(tree)
    i = 0
    for job in tqdm(jobs, ascii=True, desc='qsub'):
        if i > num_runs_for_qsub:
            break
        i += 1
        qsub(
            job=job, 
            exe_path=worker_node_main_path,
            queue=queue,
            dummy=use_dummy_qsub
        )
    print('Done. '+str(i)+' jobs have been submitted.')