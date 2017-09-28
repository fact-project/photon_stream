"""
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: phs.scoop.ceres2phs --ceres_dir=DIR --out_dir=DIR
"""
import docopt
import scoop
from glob import glob
from os.path import join
from os.path import exists
from os.path import basename
from os.path import dirname
from os import makedirs
import shutil
import tempfile
import photon_stream as ps
import fact

def produce_run(job):
    makedirs(job['out_dir'], exist_ok=True, mode=0o755)
    ps.production.sim.extract_single_photons(
        ceres_path=job['ceres_path'],
        out_dir=job['out_dir'],
        out_basename=job['out_basename'],
        o_path=job['o_path'],
        e_path=job['e_path'],
        java_path=job['java_path'],
        fact_tools_jar_path=job['fact_tools_jar_path'],
    )
    return 1


def main():
    try:
        arguments = docopt.docopt(__doc__)
        ceres_dir = arguments['--ceres_dir']
        out_dir = arguments['--out_dir']
        fact_tools_jar_path = '/home/relleums/fact-tools/target/fact-tools-0.18.1.jar'
        java_path = '/home/relleums/java8/jdk1.8.0_111'
        jobs = []

        all_ceres = glob(join(ceres_dir,'*'))
        for ceres_sub_dir in all_ceres:
            cor_basename = os.path.basename(ceres_sub_dir)
            run_number = int(cor_basename)

            all_ceres_sub_dir = glob(join(ceres_sub_dir, '*'))
            for ceres_sub_path in all_ceres_sub_dir:
                if 'Events.fits.gz' in ceres_sub_path:
                    break  

            run_number_str = '{:06d}'.format(run_number) 
            job = {
                'ceres_path': ceres_sub_path,
                'out_basename': run_number_str,
                'o_path': join(out_dir, run_number_str+'.o'),
                'e_path': join(out_dir, run_number_str+'.e'),
                'out_dir': out_dir,
                'java_path': java_path,
                'fact_tools_jar_path': fact_tools_jar_path,
            }
            print(job)
            jobs.append(job)

        job_return_codes = list(scoop.futures.map(produce_run, jobs))

    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()

