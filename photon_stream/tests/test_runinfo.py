import numpy as np
import photon_stream as ps
import pkg_resources
import os
import shutil
from glob import glob
import tempfile
import pandas as pd


old_runstatus_path = pkg_resources.resource_filename(
    'photon_stream', 
    os.path.join('tests','resources','runstatus_20161115_to_20161231.csv')
)

new_runstatus_path = pkg_resources.resource_filename(
    'photon_stream', 
    os.path.join('tests','resources','runstatus_20161115_to_20170103.csv')
)

runinfo_path = pkg_resources.resource_filename(
    'photon_stream', 
    os.path.join('tests','resources','runinfo_20161115_to_20170103.csv')
)


def test_old_runstatus_has_correct_keys():
    rs = ps.production.runinfo.read(old_runstatus_path)
    for key in rs.keys():
        assert key in ps.production.runinfo.RUNSTATUS_KEYS


def test_new_runstatus_has_correct_keys():
    rs = ps.production.runinfo.read(new_runstatus_path)
    for key in rs.keys():
        assert key in ps.production.runinfo.RUNSTATUS_KEYS


def test_append_runstatus():
    old_rs = ps.production.runinfo.read(old_runstatus_path)
    new_rs = ps.production.runinfo.read(new_runstatus_path)

    assert new_rs.shape[0] > old_rs.shape[0]

    mer_rs = ps.production.runinfo.append_new_runstatus(
        old_runstatus=old_rs,
        new_runstatus=new_rs,
    )

    runs_in_new = new_rs.shape[0]
    cols_in_old = old_rs.shape[1]

    assert mer_rs.shape[0] == runs_in_new
    assert mer_rs.shape[1] == cols_in_old

    for i, row in mer_rs.iterrows():
        if i < old_rs.shape[0]:
            for key in ps.production.runinfo.RUNSTATUS_KEYS:
                if np.isnan(mer_rs[key][i]):
                    assert np.isnan(old_rs[key][i])
                else:
                    assert mer_rs[key][i] == old_rs[key][i]
        else:
            for key in ps.production.runinfo.RUNSTATUS_KEYS:
                if np.isnan(mer_rs[key][i]):
                    assert np.isnan(new_rs[key][i])
                else:
                    assert mer_rs[key][i] == new_rs[key][i]


def test_remove_from_first_when_also_in_second():

    all_runjobs = pd.DataFrame(
        [
            {'fNight':100,'fRunID':1,'ffoo':1},
            {'fNight':100,'fRunID':2,'ffoo':2},
            {'fNight':100,'fRunID':3,'ffoo':3},
            {'fNight':101,'fRunID':1,'ffoo':4}, #out
            {'fNight':101,'fRunID':2,'ffoo':5}, 
            {'fNight':101,'fRunID':3,'ffoo':6}, #out
            {'fNight':102,'fRunID':1,'ffoo':7}, 
            {'fNight':102,'fRunID':2,'ffoo':8}, #out
            {'fNight':102,'fRunID':3,'ffoo':9},
        ]
    )

    runqstat = pd.DataFrame(
        [
            {'fNight':101,'fRunID':1,'state':'a'},
            {'fNight':101,'fRunID':3,'state':'b'},
            {'fNight':102,'fRunID':2,'state':'c'},
        ]
    )

    r = ps.production.runinfo.remove_from_first_when_also_in_second(
        first=all_runjobs, 
        second=runqstat
    )

    assert 'fNight' in r
    assert 'fRunID' in r
    assert 'ffoo' in r

    mask = np.array([1,1,1,0,1,0,1,0,1], dtype=np.bool)
    expected = all_runjobs[mask]

    print('result\n',r)
    print('expected\n',expected)

    assert len(expected) == len(r)
    for i in range(len(r)):
        assert r['fNight'].values[i] == expected['fNight'].values[i]
        assert r['fRunID'].values[i] == expected['fRunID'].values[i]
    

def test_drs_run_assignment():

    ri = ps.production.runinfo.read(runinfo_path)
    ro = ps.production.runinfo.assign_drs_runs(ri)

    for i, row in ri.iterrows():
        assert row.fNight == ro.loc[i, 'fNight']
        assert row.fRunID == ro.loc[i, 'fRunID']

        if row.fRunTypeKey == ps.production.runinfo.OBSERVATION_RUN_TYPE_KEY:

            first_method_drs_run_id = ps.production.runinfo._drs_fRunID_for_obs_run(
                runinfo=ri, fNight=row.fNight, fRunID=row.fRunID
            )
            second_method_drs_run_id = ro.loc[i, 'DrsRunID']
                
            #print(row.fNight, row.fRunID, 'old', first_method_drs_run_id, 'new', second_method_drs_run_id)
            if np.isnan(first_method_drs_run_id):
                assert np.isnan(second_method_drs_run_id)
            else:
                assert first_method_drs_run_id == second_method_drs_run_id