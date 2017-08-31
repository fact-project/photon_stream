import subprocess as sp
import pandas as pd
from io import StringIO


def qsub_job_id_from_qsub_stdout(out):
    words = out.split(' ')
    assert words[0] == 'Your'
    assert words[1] == 'job'
    assert words[4] == 'has'
    assert words[5] == 'been'
    assert words[6] == 'submitted'
    return int(words[2])


def qstat():
    try:
        out = sp.check_output(['qstat'], stderr=sp.STDOUT)
    except sp.CalledProcessError as e:
        print('returncode', e.returncode)
        print('output', e.output)
        raise _qstat_stdout_2_dataframe(out)
    

def _qstat_stdout_2_dataframe(stdout):
	return pd.read_csv(
		StringIO(stdout), 
		delim_whitespace=True, 
		skiprows=[1]
	)