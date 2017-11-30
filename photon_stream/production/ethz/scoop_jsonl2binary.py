"""
Call with 'python -m scoop --hostfile scoop_hosts.txt'

Usage: phs.scoop.jsonl.2.phs --obs_dir=DIR --out_dir=DIR

Options:
    --obs_dir=DIR   The input phs/obs/ directory with the '.phs.jsonl' runs
    --out_dir=DIR   The outpub binary directory
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


def jsonl_to_phs(job):
    try:
        with tempfile.TemporaryDirectory(prefix='phs_jsonl2binary_') as tmp:
            tmp_phs_path = join(tmp, basename(job['phs_path']))
            ps.jsonl2binary(input_path=job['jsonl_path'], output_path=tmp_phs_path)
            makedirs(dirname(job['phs_path']), exist_ok=True, mode=0o755)
            shutil.move(tmp_phs_path, job['phs_path'])
    except Exception as e:
        print(job['jsonl_path'], e)
    return 1


def main():
    try:
        arguments = docopt.docopt(__doc__)
        obs_dir = arguments['--obs_dir']
        out_dir = arguments['--out_dir']

        jobs = []
        for jsonl_path in glob(join(obs_dir, '*', '*', '*', '*.phs.jsonl.gz')):
            p = fact.path.parse(jsonl_path)
            phs_path = fact.path.tree_path(p['night'], p['run'], out_dir, '.phs.gz')
            if not exists(phs_path):
                jobs.append({'jsonl_path': jsonl_path, 'phs_path': phs_path})

        job_return_codes = list(scoop.futures.map(jsonl_to_phs, jobs))

    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()
