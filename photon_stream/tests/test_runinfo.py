import numpy as np
import photon_stream as ps
import pkg_resources


known_runs_path = pkg_resources.resource_filename(
    'photon_stream', 
    'tests/resources/known_runs_20110101.msg'
)

runinfo_path = pkg_resources.resource_filename(
    'photon_stream', 
    'tests/resources/runinfo_20120201.msg'
)


def test_known_runs_20110101_has_correct_keys():
    known_runs = ps.production.runinfo.read_runinfo_from_file(known_runs_path)
    for key in known_runs.keys():
        assert key in (
            ps.production.runinfo.ID_RUNINFO_KEYS + 
            ps.production.runinfo.TYPE_RUNINFO_KEYS +
            ps.production.runinfo.TRIGGER_NUMBER_RUNINFO_KEYS + 
            ps.production.runinfo.PHS_RUNINFO_KEYS
        )


def test_runinfo_20120201_has_correct_keys():
    runinfo = ps.production.runinfo.read_runinfo_from_file(runinfo_path)
    for key in runinfo.keys():
        assert key in (
            ps.production.runinfo.ID_RUNINFO_KEYS + 
            ps.production.runinfo.TYPE_RUNINFO_KEYS +
            ps.production.runinfo.TRIGGER_NUMBER_RUNINFO_KEYS
        )


def test_append_runinfo():
    known_runs = ps.production.runinfo.read_runinfo_from_file(known_runs_path)
    runinfo = ps.production.runinfo.read_runinfo_from_file(runinfo_path)

    new_known_runs = ps.production.runinfo.append_runinfo_to_known_runs(
        runinfo=runinfo,
        known_runs=known_runs,
    )

    runs_in_fresh_runinfo = runinfo.shape[0]
    columns_in_known_runs = known_runs.shape[1]

    assert new_known_runs.shape[0] == runs_in_fresh_runinfo
    assert new_known_runs.shape[1] == columns_in_known_runs

    for i, row in new_known_runs.iterrows():
        if i < known_runs.shape[0]:
            for id_key in ps.production.runinfo.ID_RUNINFO_KEYS:
                assert new_known_runs[id_key][i] == known_runs[id_key][i]

            for type_key in ps.production.runinfo.TYPE_RUNINFO_KEYS:
                assert new_known_runs[type_key][i] == known_runs[type_key][i]

            for phs_key in ps.production.runinfo.PHS_RUNINFO_KEYS:
                assert new_known_runs[phs_key][i] == known_runs[phs_key][i]
        else:
            for phs_key in ps.production.runinfo.PHS_RUNINFO_KEYS:
                assert new_known_runs[phs_key][i] == 0


def test_expected_number_of_triggers():
    known_runs = ps.production.runinfo.read_runinfo_from_file(known_runs_path)

    num_expected_phs_trigger = ps.production.runinfo.number_expected_phs_events(
        known_runs
    )

    num_actual_phs_trigger = known_runs['PhotonStreamNumEvents'].values

    for i, row in known_runs.iterrows():

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