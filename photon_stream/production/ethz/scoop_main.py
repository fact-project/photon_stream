"""
Usage: scoop_produce_phs --out_dir=DIR [--start_night=NIGHT] [--end_night=NIGHT] --fact_raw_dir=DIR --fact_drs_dir=DIR --fact_aux_dir=DIR --fact_tools_jar_path=PATH --fact_tools_xml_path=PATH --java_path=PATH [--tmp_dir_base_name=BASE] [--only_a_fraction=FACTOR] (--run_info_path=PATH | --fact_password=PASSWORD)

Options:
    --out_dir=DIR
    --start_night=NIGHT         [default: 20150101]
    --end_night=NIGHT           [default: 20150102]
    --only_a_fraction=FACTOR    [default: 1.0]
    --fact_raw_dir=DIR          [default: /data/fact_data]
    --fact_drs_dir=DIR          [default: /data/fact_drs.fits]
    --fact_aux_dir=DIR          [default: /data/fact_aux]
    --fact_tools_jar_path=PATH  [default: /home/relleums/fact-tools/target/fact-tools-0.18.1.jar]
    --fact_tools_xml_path=PATH  [default: /home/relleums/photon_stream/photon_stream/production/resources/observations_pass4.xml]
    --java_path=PATH            [default: /home/relleums/java8/jdk1.8.0_111]
    --tmp_dir_base_name=BASE    [default: phs_obs_]
    --run_info_path=PATH
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
import subprocess
import tempfile
import shutil


def run_job(job):

    my_env = os.environ.copy()
    my_env["PATH"] = job['java_path'] + my_env["PATH"]

    os.makedirs(job['std_yyyy_mm_nn_dir'], exist_ok=True, mode=0o755)

    with tempfile.TemporaryDirectory(prefix=job['worker_tmp_dir_base_name']) as tmp:
         with open(job['std_out_path'], 'w') as stdout, open(job['std_err_path'], 'w') as stderr:
            rc = subprocess.call(
                [
                    join(job['java_path'], 'bin', 'java'),
                    '-XX:MaxHeapSize=1024m',
                    '-XX:InitialHeapSize=512m',
                    '-XX:CompressedClassSpaceSize=64m',
                    '-XX:MaxMetaspaceSize=128m',
                    '-XX:+UseConcMarkSweepGC',
                    '-XX:+UseParNewGC',
                    '-jar',
                    job['fact_tools_jar_path'],
                    job['fact_tools_xml_path'],
                    '-Dinfile=file:'+job['raw_path'],
                    '-Ddrsfile=file:'+job['drs_path'],
                    '-Daux_dir=file:'+job['aux_dir'],
                    '-Dout_path_basename=file:'+join(tmp, job['base_name'])
                ],
                stdout=stdout,
                stderr=stderr,
                env=my_env,
            )

            for intermediate_file_path in glob.glob(join(tmp, '*')):
                if os.path.isfile(intermediate_file_path):
                    os.makedirs(job['obs_yyyy_mm_nn_dir'], exist_ok=True, mode=0o755)
                    shutil.copy(intermediate_file_path, job['obs_yyyy_mm_nn_dir'])
    return rc


def main():
    try:
        arguments = docopt.docopt(__doc__)

        if arguments['--run_info_path']:
            runinfo = ps.production.runinfo.read(
                arguments['--run_info_path']
            )
        else:
            os.environ["FACT_PASSWORD"] = arguments['--fact_password']
            runinfo = ps.production.runinfo.download_latest()

        jobs, tree = ps.production.prepare.jobs_and_directory_tree(
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
            runinfo=runinfo,
        )
        ps.production.prepare.output_tree(tree)
        job_return_codes = list(scoop.futures.map(run_job, jobs))

    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()
