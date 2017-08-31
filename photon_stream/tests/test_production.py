import numpy as np
import photon_stream as ps
import tempfile
import os
from os.path import join
from os.path import exists
import pkg_resources
import glob


def test_production_write_worker_script():
    with tempfile.TemporaryDirectory(prefix='photon_stream_test_production') as tmp:
        worker_script_path = join(tmp, 'worker.sh')
        ps.production.isdc.write_worker_script(worker_script_path)
        assert os.path.exists(worker_script_path)
        assert os.access(worker_script_path, os.X_OK)


def test_production_run_collection():
    with tempfile.TemporaryDirectory(prefix='photon_stream_run_collection') as tmp:

        runinfo_path = pkg_resources.resource_filename(
            'photon_stream', 
            'tests/resources/runinfo_2014Dec15_2015Jan15.csv')

        runinfo = ps.production.runinfo.read_runinfo_from_file(runinfo_path)

        fact_dir = join(tmp, 'fact')
        ps.production.runinfo.create_fake_fact_dir(fact_dir, runinfo)

        my_fact_tools_jar_path = join(tmp, 'my_fact_tools.jar')
        with open(my_fact_tools_jar_path, 'w') as fftools:
            fftools.write('Hi, I am a fact tools dummy java jar!')

        my_fact_tools_xml_path = join(tmp, 'observations_passX.xml')
        with open(my_fact_tools_xml_path, 'w') as fxml:
            fxml.write('Hi, I am a fact tools xml steering dummy!')

        out_dir = join(tmp, 'passX')

        # FIRST CHUNK
        ps.production.isdc.qsub(
            out_dir=out_dir, 
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
            runinfo=runinfo,
        )

        assert exists(join(tmp, 'passX', 'resources'))
        all_dirs_in_resources = glob.glob(join(tmp, 'passX', 'resources', '*'))
        assert len(all_dirs_in_resources) == 1
        current_res_dir = all_dirs_in_resources[0]
        assert exists(join(tmp, 'passX', 'resources', current_res_dir, 'observations_passX.xml'))
        assert exists(join(tmp, 'passX', 'resources', current_res_dir, 'my_fact_tools.jar'))

        #input('Take a look into '+tmp+' or press any key to continue')

        my_2nd_fact_tools_jar_path = join(tmp, 'my_2nd_fact_tools.jar')
        with open(my_2nd_fact_tools_jar_path, 'w') as fftools:
            fftools.write('Hi, I am another fact tools dummy java jar!')    

        # SECOND CHUNK with 2nd fact-tools.jar
        ps.production.isdc.qsub(
            out_dir=out_dir, 
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
            runinfo=runinfo,
        )

        all_dirs_in_resources = glob.glob(join(tmp, 'passX', 'resources', '*'))
        assert len(all_dirs_in_resources) == 2
        all_dirs_in_resources.sort()
        current_res_dir = all_dirs_in_resources[1]
        assert exists(join(tmp, 'passX', 'resources', current_res_dir, 'observations_passX.xml'))
        assert exists(join(tmp, 'passX', 'resources', current_res_dir, 'my_2nd_fact_tools.jar'))

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