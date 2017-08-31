from tqdm import tqdm
import os
import subprocess as sp
from .dummy_qsub import dummy_qsub
from .. import prepare
from .write_worker_script import write_worker_script
import pandas as pd


def qsub(
    out_dir,
    start_night=20110101,
    end_night=20501231,
    only_a_fraction=1.0,
    fact_raw_dir='/fact/raw',
    fact_drs_dir='/fact/raw',
    fact_aux_dir='/fact/aux',
    java_path='/home/guest/relleums/java8/jdk1.8.0_111',
    fact_tools_jar_path='/home/guest/relleums/fact_photon_stream/fact-tools/target/fact-tools-0.18.0.jar',
    fact_tools_xml_path='/home/guest/relleums/fact_photon_stream/photon_stream/photon_stream/production/resources/observations_pass4.xml',
    tmp_dir_base_name='fact_photon_stream_JOB_ID_',
    runinfo=None,
    queue='fact_medium', 
    use_dummy_qsub=False,
):
    job_structure = prepare.make_job_list(
        out_dir=out_dir,
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
        runinfo=runinfo,
    )
    jobs = job_structure['jobs']
    prepare.prepare_directory_structure(job_structure['directory_structure'])
    prepare.copy_resources(job_structure['directory_structure'])

    qsub2run = []

    for job in tqdm(jobs):

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
            out_dir=job['phs_yyyy_mm_nn_dir'],
            out_base_name=job['base_name'],
            tmp_dir_base_name=job['worker_tmp_dir_base_name'],
        )

        cmd = [ 
            'qsub',
            '-q', queue,
            '-o', job['std_out_path'],
            '-e', job['std_err_path'],
            job['job_path']
        ]
   
        if use_dummy_qsub:
            qsub_job_id = dummy_qsub(cmd)
        else:
            try:
                out = sp.check_output(cmd, stderr=sp.STDOUT)
                qsub_job_id = qsub_job_id_from_qsub_stdout(out)
            except sp.CalledProcessError as e:
                print('returncode', e.returncode)
                print('output', e.output)
                raise

        qsub2run.append(
            {
                'QsubID': qsub_job_id,
                'fNight': job['Night'],
                'fRunID': job['Run'],
            }
        )

    return pd.DataFrame(qsub2run)


def qsub_job_id_from_qsub_stdout(out):
    words = out.split(' ')
    assert word[0] == 'Your'
    assert word[1] == 'job'
    assert word[4] == 'has'
    assert word[5] == 'been'
    assert word[6] == 'submitted'
    return int(word[2])