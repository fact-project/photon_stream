import numpy as np
import photon_stream as ps
import pkg_resources
import os

runinfo_path = pkg_resources.resource_filename(
    'photon_stream',
    os.path.join('tests', 'resources', 'runinfo_20161115_to_20170103.csv')
)

def test_drs_run_assignment():

    ri = ps.production.runinfo.read(runinfo_path)
    ro = ps.production.drs_run.assign_drs_runs(ri)

    ri = ri[(ri.fNight>20161229) & (ri.fNight<=20170102)]
    ro = ro[(ro.fNight>20161229) & (ro.fNight<=20170102)]

    for i, row in ri.iterrows():
        assert row.fNight == ro.loc[i, 'fNight']
        assert row.fRunID == ro.loc[i, 'fRunID']

        if row.fRunTypeKey == ps.production.runinfo.OBSERVATION_RUN_TYPE_KEY:

            first_method_drs_run_id = ps.production.drs_run._drs_fRunID_for_obs_run(
                runinfo=ri, fNight=row.fNight, fRunID=row.fRunID
            )
            second_method_drs_run_id = ro.loc[i, 'DrsRunID']

            if np.isnan(first_method_drs_run_id):
                assert np.isnan(second_method_drs_run_id)
            else:
                assert first_method_drs_run_id == second_method_drs_run_id
