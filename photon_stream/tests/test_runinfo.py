import numpy as np
import photon_stream as ps
import pkg_resources
import os
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
