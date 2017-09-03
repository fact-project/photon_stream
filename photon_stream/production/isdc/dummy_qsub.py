import os
import numpy as np
import json
import subprocess
import gzip

def dummy_qsub(command):
    """
    Simulates a qsub service to enable unit testing of a qsub submitter.
    photon_stream.production.submit_to_qsub.submit_to_qsub(). It simulates 
    further simulates fact-tools and its output. Asserts that the qsub 
    parameters are valid and creates a dummy output based on the input.

    Parameters
    ----------
    command         A qsub command list as it would be given to 
                    subprocess.call() in order to submitt to qsub.
    """
    assert command[0] == 'qsub'
    assert command[1] == '-q'
    queue = command[2]
    assert command[3] == '-o'
    stdout_path = command[4]
    assert command[5] == '-e'
    stderr_path = command[6]
    assert command[7] == '-N'
    job_name = command[8]
    exec_path = command[9]
    assert exec_path is not None

    with open(stdout_path, 'w') as stdout:
        stdout.write('Dummy qsub:\n')
        stdout.write('job_name: '+job_name+'\n')
        stdout.write('stdout path: '+stdout_path+'\n')
        stdout.write('stderr path: '+stderr_path+'\n')
        stdout.write('exec_path: '+exec_path+'\n')

    with open(stderr_path, 'w') as stderr:
        pass

    out_dir = ''
    out_basename = ''
    for i, key in enumerate(command):
        if '--out_dir' in key:
            out_dir = command[i+1]
        if '--out_basename' in key:
            out_basename = command[i+1]

    assert len(out_dir) > 0
    assert len(out_basename) > 0

    os.makedirs(out_dir, exist_ok=True, mode=0o777)
    out_path = os.path.join(out_dir, out_basename)

    with gzip.open(out_path+'.phs.jsonl.gz', 'wt') as out:
        out.write('I am a dummy output photon stream\n')