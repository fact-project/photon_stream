import photon_stream as ps
import os
import pkg_resources
import qstat as qstat2dict


qstat_xml_path = pkg_resources.resource_filename(
    'photon_stream',
    os.path.join('tests', 'resources', 'qstat.xml')
)


def test_job_name_2_obs_run_id():
    name2id = ps.production.isdc.qstat.JB_name_2_run_ids
    assert name2id('phs_obs_20170101_123')['fNight'] == 20170101
    assert name2id('phs_obs_20170101_123')['fRunID'] == 123
    assert name2id('phs_obs_20170101_123')['fNight'] == 20170101
    assert name2id('phs_obs_20170101_123_lala')['fRunID'] == 123


def test_jobs_2_run_ids():
    with open(qstat_xml_path, 'rt') as fin:
        qstat_xml = fin.read()
    queue_info, job_info = qstat2dict._tools.xml2queue_and_job_info(qstat_xml)
    ids = ps.production.isdc.qstat.q_jobs_2_runqstat(
        queue_info + job_info,
        is_in_JB_name='phs_obs'
    )
    assert 'fNight' in ids
    assert 'fRunID' in ids
    assert len(ids) == 49


def test_empty_jobs_2_run_ids():
    all_jobs = []
    ids = ps.production.isdc.qstat.q_jobs_2_runqstat(
        all_jobs,
        is_in_JB_name='phs_obs'
    )
    assert 'fNight' in ids
    assert 'fRunID' in ids
    assert len(ids) == 0
