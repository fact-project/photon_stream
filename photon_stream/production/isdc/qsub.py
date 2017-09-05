import subprocess as sp
from .dummy_qsub import dummy_qsub
from os.path import exists
from os import makedirs
from os import remove
from os.path import dirname


def qsub(job, exe_path, queue, dummy=False):

    o_path = job['o_path'] if job['o_path'] is not None else '/dev/null'
    e_path = job['e_path'] if job['e_path'] is not None else '/dev/null'

    for p in [o_path, e_path]:
        if p == '/dev/null':
            continue
        if exists(p):
            remove(p)
        else:
            makedirs(dirname(p), exist_ok=True)

    cmd = [ 
        'qsub',
        '-q', queue,
        '-o', o_path,
        '-e', e_path,
        '-N', job['name'],
        exe_path
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
