import numpy as np
import photon_stream as ps
import pkg_resources
import tempfile
import gzip
import json
import os


run_path = pkg_resources.resource_filename(
    'photon_stream',
    os.path.join(
        'tests',
        'resources',
        '20170119_229_pass4_100events.phs.jsonl.gz'
    )
)


def test_number_of_events_in_file():
    assert ps.production.tools.number_of_events_in_file(run_path) == 100


old_runstatus_path = pkg_resources.resource_filename(
    'photon_stream',
    os.path.join('tests', 'resources', 'runstatus_20161115_to_20161231.csv')
)

new_runstatus_path = pkg_resources.resource_filename(
    'photon_stream',
    os.path.join('tests', 'resources', 'runstatus_20161115_to_20170103.csv')
)


def test_append_runstatus():
    old_rs = ps.production.runinfo.read(old_runstatus_path)
    new_rs = ps.production.runinfo.read(new_runstatus_path)

    assert new_rs.shape[0] > old_rs.shape[0]

    mer_rs = ps.production.runstatus._append_new_runstatus(
        old_runstatus=old_rs,
        new_runstatus=new_rs,
    )

    runs_in_new = new_rs.shape[0]
    cols_in_old = old_rs.shape[1]

    assert mer_rs.shape[0] == runs_in_new
    assert mer_rs.shape[1] == cols_in_old

    len_diff = new_rs.shape[0] - old_rs.shape[0]

    for i, row in mer_rs.iterrows():
        print(row.fNight, row.fRunID)
        if i < len_diff:
            for key in ps.production.runinfo.RUNSTATUS_KEYS:
                if np.isnan(mer_rs[key][i]):
                    assert np.isnan(new_rs[key][i])
                else:
                    assert mer_rs[key][i] == new_rs[key][i]
        else:
            for key in ps.production.runinfo.RUNSTATUS_KEYS:
                if np.isnan(mer_rs[key][i]):
                    assert np.isnan(old_rs[key][i-len_diff])
                else:
                    assert mer_rs[key][i] == old_rs[key][i-len_diff]
