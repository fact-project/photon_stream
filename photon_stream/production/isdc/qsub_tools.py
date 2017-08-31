

def qsub_job_id_from_qsub_stdout(out):
    words = out.split(' ')
    assert words[0] == 'Your'
    assert words[1] == 'job'
    assert words[4] == 'has'
    assert words[5] == 'been'
    assert words[6] == 'submitted'
    return int(words[2])