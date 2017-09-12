"""
Usage: phs.sim.production.worker [options]

Options:
    --java_path=PATH            [default: /home/guest/relleums/java8/jdk1.8.0_111]
    --fact_tools_jar_path=PATH  [default: /home/guest/relleums/fact_photon_stream/fact-tools/target/fact-tools-0.18.1.jar]
    --fact_tools_xml_path=PATH  [default: /home/guest/relleums/fact_photon_stream/photon_stream/photon_stream/production/resources/simulations_pass4.xml]
    --ceres_run_path=PATH       [default: /gpfs0/fact/processing/public/phs/sim/proton_yoda_12/205192]
    --corsika_run_path=PATH     [default: /gpfs0/fact/processing/public/phs/sim/proton_yoda_12/cer205192.gz]
    --out_dir=PATH              [default: /gpfs0/fact/processing/public/phs/sim/proton_yoda_12/205192.sim]
    --out_basename=PATH         [default: 205192]
    --tmp_dir_basename=NAME     [default: phs_sim_]
"""
import docopt
import os
from glob import glob
from os.path import join
import subprocess
import tempfile
import shutil


def run_corsika_header_extraction(
    corsika_run_path,
    corsika_run_header_path
):
    


def run_single_pulse_extractor(
    java_path,
    fact_tools_jar_path,
    fact_tools_xml_path,
    ceres_path,
    out_dir,
    out_basename,
    tmp_dir_basename,
):
    with tempfile.TemporaryDirectory(prefix=tmp_dir_basename) as tmp:

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
            '-Dout_path_basename=file:'+join(tmp, out_basename),
        ])  

        for intermediate_file_path in glob(join(tmp, '*')):
            if os.path.isfile(intermediate_file_path):
                os.makedirs(out_dir, exist_ok=True, mode=0o755)
                shutil.copy(intermediate_file_path, out_dir)






"""
java -jar fact-tools-0.18.0.jar 
../../photon_stream/photon_stream/production/resources/simulations_pass4.xml 
-Dinfile=file:../../run_Mars/00000003.014_D_MonteCarlo011_Events.fits 
-Dout_path_basename=file:../../photon_stream/photon_stream/tests/resources/cer011014
"""
