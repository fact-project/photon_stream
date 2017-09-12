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


def extract_single_photons(
    ceres_path,
    out_dir,
    out_basename,
    java_path='/home/guest/relleums/java8/jdk1.8.0_111',
    fact_tools_jar_path='/home/guest/relleums/fact_photon_stream/fact-tools/target/fact-tools-0.18.1.jar',
    mc_drs_file='/home/guest/relleums/fact_photon_stream/fact-tools/src/main/resources/testMcDrsFile.drs.fits.gz',
    fact_tools_xml_path=fact_tools_xml_path,
    tmp_dir_prefix='phs_sim_produce_',
):
    with tempfile.TemporaryDirectory(prefix=tmp_dir_prefix) as tmp:

        my_env = os.environ.copy()
        my_env["PATH"] = java_path + my_env["PATH"]

        cmd = [
            'java',
            '-XX:MaxHeapSize=1024m',
            '-XX:InitialHeapSize=512m',
            '-XX:CompressedClassSpaceSize=64m',
            '-XX:MaxMetaspaceSize=128m',
            '-XX:+UseConcMarkSweepGC',
            '-XX:+UseParNewGC',
            '-jar', fact_tools_jar_path, fact_tools_xml_path,
            '-Dinfile=file:'+ceres_path,
            '-Ddrsfile=file:'+mc_drs_file,
            '-Dout_path_basename='+join(tmp, out_basename),
        ]
        for k in cmd:
            print(k)
        input('wait')
        subprocess.call(cmd)

        for tmp_path in glob(join(tmp, '*')):
            if os.path.isfile(tmp_path):
                os.makedirs(out_dir, exist_ok=True, mode=0o755)
                shutil.copy(tmp_path, out_dir)