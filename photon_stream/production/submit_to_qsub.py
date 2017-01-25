import os
from tqdm import tqdm
import subprocess as sp

from .runinfo import get_runinfo
from . import tools
from .write_worker_script import write_worker_script
from .runinfo import observation_runs_in_runinfo_in_night_range
from .runinfo import add_drs_run_info_to_jobs

def submit_to_qsub(
    out_dir, 
    start_nigth=20110101, 
    end_nigth=20501231,
    fact_dir='/fact/', 
    java_path='/home/guest/relleums/java8/jdk1.8.0_111',
    fact_tools_jar_path='/home/guest/relleums/fact_photon_stream/fact-tools/target/fact-tools-0.18.0.jar',
    fact_tools_xml_path='/home/guest/relleums/fact_photon_stream/photon_stream/photon_stream/production/observations_pass3.xml',
    tmp_dir_base_name='fact_photon_stream_JOB_ID_',
    queue='fact_medium', 
    email='sebmuell@phys.ethz.ch',
    print_only=True,
    runinfo=None):
    
    print('Start single pulse conversion ...')

    out_dir = os.path.abspath(out_dir)
    fact_dir = os.path.abspath(fact_dir)

    if runinfo is None:
        runinfo = get_runinfo()
    
    std_dir = os.path.join(out_dir, 'std')
    jobs_dir = os.path.join(out_dir, 'jobs')
    scripts_dir = os.path.join(out_dir, 'worker_scripts')

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(std_dir, exist_ok=True)
    os.makedirs(jobs_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)

    print('Find runs in night range '+str(start_nigth)+' to '+str(end_nigth)+' in runinfo database ...')
    
    jobs = observation_runs_in_runinfo_in_night_range(
        runinfo=runinfo,
        start_nigth=start_nigth, 
        end_nigth=end_nigth)

    print('Found '+str(len(jobs))+' runs in database.')
    print('Find intersection with runs accessible in "'+fact_dir+'" ...')

    for job in jobs:
        job['yyyy'] = tools.night_id_2_yyyy(job['Night'])
        job['mm'] = tools.night_id_2_mm(job['Night'])
        job['nn'] = tools.night_id_2_nn(job['Night'])
        job['fact_dir'] = fact_dir
        job['yyyymmnn_dir'] = '{y:04d}/{m:02d}/{n:02d}/'.format(
            y=job['yyyy'],
            m=job['mm'],
            n=job['nn'])
        job['base_name'] = '{bsn:08d}_{rrr:03d}'.format(
            bsn=job['Night'],
            rrr=job['Run'])
        job['raw_file_name'] = job['base_name']+'.fits.fz'
        job['raw_path'] = os.path.join(
            job['fact_dir'], 
            'raw', 
            job['yyyymmnn_dir'], 
            job['raw_file_name'])
        job['aux_dir'] = os.path.join(
            job['fact_dir'], 
            'aux', 
            job['yyyymmnn_dir'])

    jobs = tools.jobs_where_path_exists(jobs, path='raw_path')

    print('Found '+str(len(jobs))+' runs both in database and accesible in "'+fact_dir+'".')
    print('Find matching drs calibration runs ...')

    jobs = add_drs_run_info_to_jobs(runinfo=runinfo, jobs=jobs)
    jobs = tools.jobs_where_path_exists(jobs=jobs, path='drs_path')

    print('Found '+str(len(jobs))+' with accesible drs files.')
    print('Submitt jobs into qsub ...')

    for job in tqdm(jobs): 
        job['std_dir'] = std_dir
        job['stdout_path'] = os.path.join(std_dir, job['base_name']+'.o')
        job['stderr_path'] = os.path.join(std_dir, job['base_name']+'.e')
        job['jobs_dir'] = jobs_dir
        job['job_path'] = os.path.join(jobs_dir, job['base_name']+'_job.json')
        
        job['worker_script_path'] = os.path.join(scripts_dir, 'PhotonStream_'+job['base_name']+'.sh')
        job['worker_tmp_dir_base_name'] = tmp_dir_base_name
        job['email'] = email
        job['queue'] = queue

        job['java_path'] = java_path
        job['fact_tools_jar_path'] = fact_tools_jar_path
        job['fact_tools_xml_path'] = fact_tools_xml_path

        job['out_dir'] = os.path.join(out_dir, job['yyyymmnn_dir'])

        write_worker_script(
            path=job['worker_script_path'],
            java_path=job['java_path'],
            fact_tools_jar_path=job['fact_tools_jar_path'],
            fact_tools_xml_path=job['fact_tools_xml_path'],
            in_run_path=job['raw_path'],
            drs_path=job['drs_path'],
            aux_dir=job['aux_dir'],
            out_dir=job['out_dir'],
            out_base_name=job['base_name'],
            tmp_dir_base_name=job['worker_tmp_dir_base_name'],)

        cmd = [ 'qsub',
                '-q', queue,
                '-o', job['stdout_path'],
                '-e', job['stderr_path'],
                '-m', 'ae', # send email in case of (e)nd or (a)bort
                '-M', email,
                job['worker_script_path']]
   
        if print_only:
            print(cmd)
        else:
            sp.check_output(cmd)

        tools.write_json(job['job_path'], job)
        print('Done.')