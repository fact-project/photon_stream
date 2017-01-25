import numpy as np
import photon_stream as ps
import tempfile
import os
import pkg_resources


def test_production_write_worker_script():
    with tempfile.TemporaryDirectory(prefix='photon_stream_test_production') as tmp:
        worker_script_path = os.path.join(tmp, 'worker.sh')
        ps.production.write_worker_script(worker_script_path)
        assert os.path.exists(worker_script_path)
        assert os.access(worker_script_path, os.X_OK)


def test_production_run_collection():
    with tempfile.TemporaryDirectory(prefix='photon_stream_run_collection') as tmp:

        runinfo_path = pkg_resources.resource_filename(
            'photon_stream', 
            'tests/resources/runinfo_2014Dec15_2015Jan15.msg')

        runinfo = ps.production.runinfo.read_runinfo_from_file(runinfo_path)

        fact_dir = os.path.join(tmp, 'fact')
        ps.production.runinfo.create_fake_fact_dir(fact_dir, runinfo)

        out_dir = os.path.join(tmp, 'production_output')
        ps.production.submit_to_qsub(
            out_dir=out_dir, 
            start_nigth=20141215, 
            end_nigth=20150103,
            fact_dir=fact_dir, 
            java_path='/usr/java/jdk1.8.0_77/bin',
            fact_tools_jar_path='my_fact_tools.jar',
            fact_tools_xml_path='my_observations_pass3.xml',
            tmp_dir_base_name='fact_photon_stream_JOB_ID_',
            queue='fact_medium', 
            email='sebmuell@phys.ethz.ch',
            print_only=True,
            runinfo=runinfo)

        # input('Take a look into '+tmp+' or press any key to continue')

