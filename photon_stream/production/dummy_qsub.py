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
    assert command[7] == '-m'
    assert command[8] == 'ae'
    assert command[9] == '-M'
    email = command[10]
    job_path = command[11]

    with open(stdout_path, 'w') as stdout:
        stdout.write('Dummy qsub:\n')
        stdout.write('stdout path: '+stdout_path+'\n')
        stdout.write('stderr path: '+stderr_path+'\n')
        stdout.write('email: '+email+'\n')
        stdout.write('job path: '+job_path+'\n')

    with open(stderr_path, 'w') as stderr:
        pass

    out_dir, out_base_name = extract_out_path_from_worker_job(job_path)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, out_base_name)

    with gzip.open(out_path+'.phs.jsonl.gz', 'wt') as out:
        out.write('I am a dummy output photon stream\n')


def extract_out_path_from_worker_job(job_path):
    with open(job_path, 'r') as job:
        out_base_name = ''
        out_dir = ''
        for line in job:
            if '-Dout_path_basename=file:$TMP_DIR' in line:
                out_base_name = line[38:38+(8+1+3)]
            if 'mkdir -p' in line:
                out_dir = line[9:]
                if out_dir[-1] == '\n':
                    out_dir = out_dir[:-1]
    return [out_dir, out_base_name]