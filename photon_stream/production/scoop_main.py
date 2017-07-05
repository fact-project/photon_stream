"""
Usage: scoop_produce_phs --out_dir=DIR --start_night=NIGHT --end_night=NIGHT --fact_raw_dir=DIR --fact_drs_dir=DIR --fact_aux_dir=DIR --fact_tools_jar_path=PATH --fact_tools_xml_path=PATH --java_path=PATH --tmp_dir_base_name=BASE --only_a_fraction=FACTOR --only_append=BOOL --fact_password=PASSWORD

Options:
    --out_dir=DIR
    --start_night=NIGHT [default: 20150101]
    --end_night=NIGHT [default: 20150102]
    --only_a_fraction=FACTOR [default: 1.0]
    --fact_raw_dir=DIR [default: /data/fact_data]
    --fact_drs_dir=DIR [default: /data/fact_drs.fits]
    --fact_aux_dir=DIR [default: /data/fact_aux]
    --fact_tools_jar_path=PATH [default: /home/relleums/fact-tools/target/fact-tools-0.18.0.jar]
    --fact_tools_xml_path=PATH [default: /home/relleums/photon_stream/photon_stream/production/observations_pass4.xml]
    --java_path=PATH [default: /home/relleums/java8/jdk1.8.0_111]
    --tmp_dir_base_name=BASE  [default: fact_photon_stream_JOB_ID_]  
    --only_append=BOOL [default: True]
    --fact_password=PASSWORD
"""
import docopt
import scoop
import os
import glob
import photon_stream as ps
from os.path import join
from os.path import split
from os.path import exists

def run_job(job):
    ps.production.write_worker_script(
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

    job_return_code = subprocess.call(
        job['job_path'], 
        stdout=job['stdout_path'], 
        stderr=job['stderr_path'],
    )

    return job_return_code


def main():
    try:
        arguments = docopt.docopt(__doc__)

        if arguments['--only_append'] == 'True':
            only_append = True
        elif arguments['--only_append'] == 'False':
            only_append = False
        else:
            raise ValueError("--only_append must be either 'True' or 'False'.")

        subprocess.call(
            ['export', 'FACT_PASSWORD='+arguments['--fact_password']]
        )

        jobs = ps.production.make_job_list(
            out_dir=arguments['--out_dir'],
            start_night=int(arguments['--start_night']),
            end_night=int(arguments['--end_night']),
            only_a_fraction=float(arguments['--only_a_fraction']),
            fact_raw_dir=arguments['--fact_raw_dir'],
            fact_drs_dir=arguments['--fact_drs_dir'],
            fact_aux_dir=arguments['--fact_aux_dir'],
            java_path=arguments['--java_path'],
            fact_tools_jar_path=arguments['--fact_tools_jar_path'],
            fact_tools_xml_path=arguments['--fact_tools_xml_path'],
            tmp_dir_base_name=arguments['--tmp_dir_base_name'],
            runinfo=None,
            only_append=only_append,
        )

        job_return_codes = list(scoop.futures.map(run_job, jobs))

    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()