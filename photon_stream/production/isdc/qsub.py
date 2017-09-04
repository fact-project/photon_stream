
import subprocess as sp
from .dummy_qsub import dummy_qsub
from os.path import exists
from os import makedirs
from os import remove


def qsub(job, exe_path, dummy=False):

    for p in [job['o_path'], job['e_path']]:
        if exists(p):
            remove(p)
        else:
            makedirs(dirname(p), exist_ok=True)

    cmd = [ 
        'qsub',
        '-q', queue,
        '-o', job['o_path'],
        '-e', job['e_path'],
        '-N', job['name'],
        which(exe_path)
    ]
    for key in job:
        if '--' in key:
            cmd += [key, job[key]] 

    if dummy:
        dummy_qsub(cmd)
    else:
        try:
            sp.check_output(cmd, stderr=sp.STDOUT)
        except sp.CalledProcessError as e:
            print('returncode', e.returncode)
            print('output', e.output)
            raise
