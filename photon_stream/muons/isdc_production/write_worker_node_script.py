import os, stat


def write_worker_node_script(
    path,
    input_run_path,
    output_muon_path):
    """
    Writes an executable bash script for a worker node to extract the muons
    from one fact photon-stream run.
    """
    sh = '#!/bin/bash\n'
    sh += 'source /home/guest/relleums/.bashrc\n'
    sh += 'eval "phs_extract_muons'
    sh += ' -i ' + input_run_path
    sh += ' -o ' + output_muon_path + '"\n'
    with open(path, 'w') as fout:
        fout.write(sh)

    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
