import os
from glob import glob
from os.path import join
import subprocess
import tempfile
import shutil
import pkg_resources

fact_tools_xml_path = pkg_resources.resource_filename(
    'photon_stream', 
    os.path.join('production','resources','simulations_pass4.xml')
)

mc_drs_path = pkg_resources.resource_filename(
    'photon_stream', 
    os.path.join('production','resources','testMcDrsFile.drs.fits.gz')
)


def extract_single_photons(
    ceres_path,
    out_dir,
    out_basename,
    java_path='/home/guest/relleums/java8/jdk1.8.0_111',
    fact_tools_jar_path='/home/guest/relleums/fact_photon_stream/fact-tools/target/fact-tools-0.18.1.jar',
    fact_tools_xml_path=fact_tools_xml_path,
    mc_drs_path=mc_drs_path,
    tmp_dir_prefix='phs_sim_produce_',
):
    """
    Apply the fact-tools single pulse extractor to a simulation run.
    Creates a phs (photon-stream) file and a baseline offset file which is 
    hopefully useless.

    ceres_path      The FACT raw simulation fits file with the instrument 
                    responses.

    out_dir         The output directory to collect the results.

    out_basename    The basename e.g. run number of the output files.
    """
    with tempfile.TemporaryDirectory(prefix=tmp_dir_prefix) as tmp:

        my_env = os.environ.copy()
        my_env["PATH"] = java_path + my_env["PATH"]

        subprocess.call([
            'java',
            '-XX:MaxHeapSize=1024m',
            '-XX:InitialHeapSize=512m',
            '-XX:CompressedClassSpaceSize=64m',
            '-XX:MaxMetaspaceSize=128m',
            '-XX:+UseConcMarkSweepGC',
            '-XX:+UseParNewGC',
            '-jar', fact_tools_jar_path, fact_tools_xml_path,
            '-Dinfile=file:'+ceres_path,
            '-Ddrsfile=file:'+mc_drs_path,
            '-Dout_path_basename='+join(tmp, out_basename),
        ])

        for tmp_path in glob(join(tmp, '*')):
            if os.path.isfile(tmp_path):
                os.makedirs(out_dir, exist_ok=True, mode=0o755)
                shutil.copy(tmp_path, out_dir)