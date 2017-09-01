import numpy as np
import photon_stream as ps
import tempfile
import os
from os.path import join
from os.path import exists
import pkg_resources
import glob


runinfo_path = pkg_resources.resource_filename(
    'photon_stream', 
    join('tests','resources','runinfo_2014Dec15_2015Jan15.csv')
)

qstat_xml_path = pkg_resources.resource_filename(
    'photon_stream', 
    os.path.join('tests','resources','qstat.xml')
)
with open(qstat_xml_path, 'rt') as fin:
    qstat_xml = fin.read()
    runqstat = ps.production.isdc.qstat.jobs_2_run_ids(
        ps.production.isdc.qstat.jobs_in_qstatxml(qstat_xml)
    )

def test_number_of_events_in_run():
    run_path = pkg_resources.resource_filename(
        'photon_stream', 
        join('tests','resources','20170119_229_pass4_100events.phs.jsonl.gz')
    )    
    assert ps.production.status.number_of_events_in_event_list_file(run_path) == 100


def test_production_write_worker_script():
    with tempfile.TemporaryDirectory(prefix='photon_stream_test_production') as tmp:
        worker_script_path = join(tmp, 'worker.sh')
        ps.production.isdc.write_worker_script(worker_script_path)
        assert os.path.exists(worker_script_path)
        assert os.access(worker_script_path, os.X_OK)


def test_production_run_collection():
    #with tempfile.TemporaryDirectory(prefix='photon_stream_run_collection') as tmp:
    with open(runinfo_path, 'rb') as lalala:
        tmp = '/home/sebastian/Desktop/phs_production'
        os.makedirs(tmp, exist_ok=True)


        runinfo = ps.production.runinfo.read(runinfo_path)

        fact_dir = join(tmp, 'fact')
        ps.production.runinfo.create_fake_fact_dir(fact_dir, runinfo)

        my_fact_tools_jar_path = join(tmp, 'my_fact_tools.jar')
        with open(my_fact_tools_jar_path, 'w') as fftools:
            fftools.write('Hi, I am a fact tools dummy java jar!')

        my_fact_tools_xml_path = join(tmp, 'observations_passX.xml')
        with open(my_fact_tools_xml_path, 'w') as fxml:
            fxml.write('Hi, I am a fact tools xml steering dummy!')

        phs_dir = join(tmp, 'phs')

        # FIRST CHUNK
        ps.production.isdc.qsub(
            phs_dir=phs_dir, 
            start_night=20141215, 
            end_night=20141229,
            only_a_fraction=1.0,
            fact_raw_dir=join(fact_dir, 'raw'),
            fact_drs_dir=join(fact_dir, 'raw'),
            fact_aux_dir=join(fact_dir, 'aux'),
            java_path='/usr/java/jdk1.8.0_77/bin',
            fact_tools_jar_path=my_fact_tools_jar_path,
            fact_tools_xml_path=my_fact_tools_xml_path,
            tmp_dir_base_name='fact_photon_stream_JOB_ID_',
            queue='fact_medium', 
            use_dummy_qsub=True,
            qstat_dummy=runqstat,
            job_runinfo=runinfo,
            start_new=True,
        )

        assert os.path.exists(phs_dir)
        assert os.path.exists(join(phs_dir,'obs'))
        assert os.path.exists(join(phs_dir,'obs','runstatus.csv'))
        assert os.path.exists(join(phs_dir,'obs','.lock'))
        assert os.path.exists(join(phs_dir,'.obs.std'))
        assert os.path.exists(join(phs_dir,'.obs.job'))


        #input('Take a look into '+tmp+' or press any key to continue')

        my_2nd_fact_tools_jar_path = join(tmp, 'my_2nd_fact_tools.jar')
        with open(my_2nd_fact_tools_jar_path, 'w') as fftools:
            fftools.write('Hi, I am another fact tools dummy java jar!')    

        # SECOND CHUNK with 2nd fact-tools.jar
        ps.production.isdc.qsub(
            phs_dir=phs_dir, 
            start_night=20141229, 
            end_night=20150103,
            only_a_fraction=1.0,
            fact_raw_dir=join(fact_dir, 'raw'),
            fact_drs_dir=join(fact_dir, 'raw'),
            fact_aux_dir=join(fact_dir, 'aux'),
            java_path='/usr/java/jdk1.8.0_77/bin',
            fact_tools_jar_path=my_2nd_fact_tools_jar_path,
            fact_tools_xml_path=my_fact_tools_xml_path,
            tmp_dir_base_name='fact_photon_stream_JOB_ID_',
            queue='fact_medium', 
            use_dummy_qsub=True,
            qstat_dummy=runqstat,
            job_runinfo=runinfo,
            start_new=False,
        )

        #input('Take a look into '+tmp+' or press any key to continue')

def test_status_bar_string():

    progress_bar_str = ps.production.status.progress(ratio=0.0, length=50)
    assert len(progress_bar_str) < 50

    progress_bar_str = ps.production.status.progress(ratio=1.0, length=50)
    assert len(progress_bar_str) > 50    
    assert len(progress_bar_str) < 60    

    progress_bar_str = ps.production.status.progress(ratio=10.0, length=50)
    assert len(progress_bar_str) > 50    
    assert len(progress_bar_str) < 61  

    progress_bar_str = ps.production.status.progress(ratio=100.0, length=50)
    assert len(progress_bar_str) > 50    
    assert len(progress_bar_str) < 62 