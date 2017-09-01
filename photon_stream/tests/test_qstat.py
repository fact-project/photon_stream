import photon_stream as ps
import os
import pkg_resources


qstat_xml_path = pkg_resources.resource_filename(
    'photon_stream', 
    os.path.join('tests','resources','qstat.xml')
)


def test_jobs_in_qstatxml():
    with open(qstat_xml_path, 'rt') as fin:
        qstat_xml = fin.read()
    jobs = ps.production.isdc.qstat.jobs_in_qstatxml(qstat_xml)
    assert len(jobs) == 51

    for job in jobs:
        assert 'name' in job
        assert 'state' in job


def test_job_name_2_obs_run_id():
    name2id = ps.production.isdc.qstat.job_name_2_obs_run_id
    assert name2id('phs_obs_20170101_123')['fNight'] == 20170101
    assert name2id('phs_obs_20170101_123')['fRunID'] == 123
    assert name2id('phs_obs_20170101_123')['fNight'] == 20170101
    assert name2id('phs_obs_20170101_123_lala')['fRunID'] == 123


def test_jobs_2_run_ids():
    with open(qstat_xml_path, 'rt') as fin:
        qstat_xml = fin.read()
    all_jobs = ps.production.isdc.qstat.jobs_in_qstatxml(qstat_xml)
    ids = ps.production.isdc.qstat.jobs_2_run_ids(all_jobs, name='phs_obs')
    assert 'fNight' in ids
    assert 'fRunID' in ids
    assert 'state' in ids
    assert len(ids) == 48


def test_empty_jobs_2_run_ids():
    all_jobs = []
    ids = ps.production.isdc.qstat.jobs_2_run_ids(all_jobs, name='phs_obs')
    assert 'fNight' in ids
    assert 'fRunID' in ids
    assert 'state' in ids
    assert len(ids) == 0