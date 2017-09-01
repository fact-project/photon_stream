import numpy as np
import photon_stream as ps
import pkg_resources
import os
import shutil
from glob import glob
import tempfile
import pandas as pd


runstatus_path = pkg_resources.resource_filename(
    'photon_stream', 
    os.path.join('tests','resources','runstatus_20110101.csv')
)

runinfo_path = pkg_resources.resource_filename(
    'photon_stream', 
    os.path.join('tests','resources','runinfo_20120201.csv')
)


def test_runstatus_20110101_has_correct_keys():
    runstatus = ps.production.runinfo.read(runstatus_path)
    for key in runstatus.keys():
        assert key in (
            ps.production.runinfo.ID_RUNINFO_KEYS + 
            ps.production.runinfo.TYPE_RUNINFO_KEYS +
            ps.production.runinfo.TRIGGER_NUMBER_RUNINFO_KEYS + 
            ps.production.runinfo.PHS_RUNINFO_KEYS
        )


def test_runinfo_20120201_has_correct_keys():
    runinfo = ps.production.runinfo.read(runinfo_path)
    for key in runinfo.keys():
        assert key in (
            ps.production.runinfo.ID_RUNINFO_KEYS + 
            ps.production.runinfo.TYPE_RUNINFO_KEYS +
            ps.production.runinfo.TRIGGER_NUMBER_RUNINFO_KEYS
        )


def test_append_runinfo():
    runstatus = ps.production.runinfo.read(runstatus_path)
    runinfo = ps.production.runinfo.read(runinfo_path)

    new_runstatus = ps.production.runinfo.append_runinfo_to_runstatus(
        runinfo=runinfo,
        runstatus=runstatus,
    )

    runs_in_fresh_runinfo = runinfo.shape[0]
    columns_in_runstatus = runstatus.shape[1]

    assert new_runstatus.shape[0] == runs_in_fresh_runinfo
    assert new_runstatus.shape[1] == columns_in_runstatus

    for i, row in new_runstatus.iterrows():
        if i < runstatus.shape[0]:
            for id_key in ps.production.runinfo.ID_RUNINFO_KEYS:
                assert new_runstatus[id_key][i] == runstatus[id_key][i]

            for type_key in ps.production.runinfo.TYPE_RUNINFO_KEYS:
                assert new_runstatus[type_key][i] == runstatus[type_key][i]

            for phs_key in ps.production.runinfo.PHS_RUNINFO_KEYS:
                assert new_runstatus[phs_key][i] == runstatus[phs_key][i]
        else:
            for phs_key in ps.production.runinfo.PHS_RUNINFO_KEYS:
                assert new_runstatus[phs_key][i] == 0


def test_expected_number_of_triggers():
    runstatus = ps.production.runinfo.read(runstatus_path)

    num_expected_phs_trigger = ps.production.runinfo.number_expected_phs_events(
        runstatus
    )

    num_actual_phs_trigger = runstatus['PhotonStreamNumEvents'].values

    for i, row in runstatus.iterrows():

        if row['fRunTypeKey'] == ps.production.runinfo.OBSERVATION_RUN_TYPE_KEY:
            manual_expected = (
                row['fNumExt1Trigger'] + 
                row['fNumExt2Trigger'] +
                row['fNumPhysicsTrigger'] +
                row['fNumPedestalTrigger']
            )

            if np.isnan(manual_expected):
                assert num_expected_phs_trigger[i] == 0
            else:
                assert num_expected_phs_trigger[i] == manual_expected


def test_runinfo_backup():
    with tempfile.TemporaryDirectory(prefix='phs_') as tmp:
        tmp_runinfo_path = os.path.join(tmp, os.path.basename(runinfo_path))

        shutil.copy(runinfo_path, tmp_runinfo_path)
        assert os.path.exists(tmp_runinfo_path)

        def files_and_hidden_files_dir(d):
            return glob(os.path.join(d, '*')) + glob(os.path.join(d, '.*'))

        files = files_and_hidden_files_dir(tmp)
        assert len(files) == 1

        backup_path = ps.production.tools.local_backup_path_with_timestamp(tmp_runinfo_path)
        shutil.copy(tmp_runinfo_path, backup_path)

        files = files_and_hidden_files_dir(tmp)
        assert len(files) == 2

        assert tmp_runinfo_path in files
        files.remove(tmp_runinfo_path)
        assert len(files) == 1
        _backup_path = files[0]
        _backup_basename = os.path.basename(_backup_path)
        assert len(_backup_basename) > 0
        assert _backup_basename[0] == '.'


def test_obs_runs_not_in_qstat():

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

    r = ps.production.runinfo.obs_runs_not_in_qstat(
        all_runjobs=all_runjobs, 
        runqstat=runqstat
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
    
def test_remove_all_obs_runs_from_runinfo_not_in_runjobs():

    runi = pd.DataFrame(
        [
            {'fNight':100,'fRunID':1,'fRunTypeKey':2}, #keep DRS
            {'fNight':100,'fRunID':2,'fRunTypeKey':1}, #keep
            {'fNight':100,'fRunID':3,'fRunTypeKey':1}, #keep
            {'fNight':101,'fRunID':1,'fRunTypeKey':2}, #keep DRS
            {'fNight':101,'fRunID':2,'fRunTypeKey':1}, #keep
            {'fNight':101,'fRunID':3,'fRunTypeKey':1},
            {'fNight':102,'fRunID':1,'fRunTypeKey':2}, #keep DRS
            {'fNight':102,'fRunID':2,'fRunTypeKey':1},
            {'fNight':102,'fRunID':3,'fRunTypeKey':1}, #keep
        ]
    )

    runjobs = pd.DataFrame(
        [
            {'fNight':100,'fRunID':2,'fRunTypeKey':1},
            {'fNight':100,'fRunID':3,'fRunTypeKey':1},
            {'fNight':101,'fRunID':2,'fRunTypeKey':1},
            {'fNight':102,'fRunID':3,'fRunTypeKey':1},
        ]
    )

    r = ps.production.runinfo.remove_all_obs_runs_from_runinfo_not_in_runjobs(
        runinfo=runi, 
        runjobs=runjobs
    )

    assert len(r) == len(runi) - 2
    assert 'fNight' in r
    assert 'fRunID' in r
    assert 'fRunTypeKey' in r

    mask = np.array([1,1,1,1,1,0,1,0,1], dtype=np.bool)
    expected = runi[mask]

    print('result\n',r)
    print('expected\n',expected)

    assert len(expected) == len(r)
    for i in range(len(r)):
        assert r['fNight'].values[i] == expected['fNight'].values[i]
        assert r['fRunID'].values[i] == expected['fRunID'].values[i]