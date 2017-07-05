from tqdm import tqdm

from .dummy_qsub import dummy_qsub
from .make_job_list import make_job_list
from .write_worker_script import write_worker_script


def isdc(
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
    queue='fact_medium', 
    email='sebmuell@phys.ethz.ch',
    use_dummy_qsub=False,
):
    jobs = make_job_list(
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
        only_append=only_append,
    )

    for job in tqdm(jobs): 
        write_worker_script(
            path=job['job_path'],
            java_path=job['java_path'],
            fact_tools_jar_path=job['fact_tools_jar_path'],
            fact_tools_xml_path=job['fact_tools_xml_path'],
            in_run_path=job['raw_path'],
            drs_path=job['drs_path'],
            aux_dir=job['aux_dir'],
            out_dir=job['phs_dir'],
            out_base_name=job['base_name'],
            tmp_dir_base_name=job['worker_tmp_dir_base_name'],
        )

        cmd = [ 
            'qsub',
            '-q', queue,
            '-o', job['stdout_path'],
            '-e', job['stderr_path'],
            '-m', 'ae', # send email in case of (e)nd or (a)bort
            '-M', email,
            job['job_path']
        ]
   
        if use_dummy_qsub:
            dummy_qsub(cmd)
        else:
            qsub_return_code = sp.call(cmd)
            if qsub_return_code > 0:
                print('qsub return code: ', qsub_return_code)
