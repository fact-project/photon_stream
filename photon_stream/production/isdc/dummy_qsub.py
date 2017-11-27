import os
import numpy as np
import json
import subprocess
import gzip
import fact
import json


def dummy_qsub(args):
    """
    Simulates a qsub service to enable unit testing of a qsub submitter.
    photon_stream.production.submit_to_qsub.submit_to_qsub(). It simulates
    further simulates fact-tools and its output. Asserts that the qsub
    parameters are valid and creates a dummy output based on the input.

    Parameters
    ----------
    args         A qsub args list as it would be given to
                    subprocess.call() in order to submitt to qsub.
    """
    assert args[0] == 'qsub'
    assert args[1] == '-q'
    queue = args[2]
    assert args[3] == '-o'
    o_path = args[4]
    assert args[5] == '-e'
    e_path = args[6]
    assert args[7] == '-N'
    job_name = args[8]
    exec_path = args[9]
    assert exec_path is not None
    assert os.path.exists(exec_path)
    assert os.path.isabs(exec_path)
    if  'phs.isdc.obs.status.worker' in exec_path:
        assert 'phs_obs_status' in job_name
        dummy_status(args[9:], o_path, e_path)
        return
    elif 'phs.isdc.obs.produce.worker' in exec_path:
        assert 'phs_obs' in job_name
        dummy_produce(args[9:], o_path, e_path)
        return
    print('exec_path: "'+exec_path+'"')
    assert False


def dummy_produce(args, o_path, e_path):
    raw_path = ''
    out_dir = ''
    out_basename = ''
    for i, key in enumerate(args):
        if '--out_dir' in key:
            out_dir = args[i+1]
        if '--out_basename' in key:
            out_basename = args[i+1]
        if '--raw_path' in key:
            raw_path = args[i+1]
    assert len(out_dir) > 0
    assert len(out_basename) > 0
    assert len(raw_path) > 0

    os.makedirs(out_dir, exist_ok=True, mode=0o777)
    out_path = os.path.join(out_dir, out_basename)

    with open(raw_path, 'r') as raw:
        xi = json.loads(raw.read())

    xo = {'NumExpectedPhsEvents': xi['NumExpectedPhsEvents']}
    with gzip.open(out_path+'.phs.jsonl.gz', 'wt') as out:
        out.write(json.dumps(xo))

    with open(o_path, 'w') as stdout:
        stdout.write('Here dummy fact-tools tells its tail of argony and pain...\n')
        stdout.write('stdout path: '+o_path+'\n')
        stdout.write('stderr path: '+e_path+'\n')

    with open(e_path, 'w') as stderr:
        pass


def dummy_status(args, o_path, e_path):
    phs_path = ''
    status_path = ''
    for i, key in enumerate(args):
        if '--phs_path' in key:
            phs_path = args[i+1]
        if '--status_path' in key:
            status_path = args[i+1]
    assert len(phs_path) > 0
    assert len(status_path) > 0

    with gzip.open(phs_path, 'rt') as phs_in:
        actual_events = json.loads(phs_in.read())['NumExpectedPhsEvents']

    stat = {}
    r = fact.path.parse(phs_path)
    stat['fNight'] = r['night']
    stat['fRunID'] = r['run']
    stat['PhsSize'] = 1337
    stat['NumActualPhsEvents'] = actual_events

    os.makedirs(os.path.dirname(status_path), exist_ok=True, mode=0o777)
    with open(status_path, 'w') as fout:
        json.dump(stat, fout)

    with open(o_path, 'w') as o:
        o.write('status stdout')

    with open(e_path, 'w') as e:
        e.write('status stderr')