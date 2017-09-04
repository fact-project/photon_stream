#! /usr/bin/env python
"""
Usage: phs.obs.production.isdc.worker [options]

Options:
    --java_path=PATH            [default: /home/guest/relleums/java8/jdk1.8.0_111]
    --fact_tools_jar_path=PATH  [default: /home/guest/relleums/fact_photon_stream/fact-tools/target/fact-tools-0.18.1.jar]
    --fact_tools_xml_path=PATH  [default: /home/guest/relleums/fact_photon_stream/photon_stream/photon_stream/production/resources/observations_pass4.xml]
    --raw_path=PATH             [default: /fact/raw/2017/09/01/20170901_139.fits.fz]
    --drs_path=PATH             [default: /fact/raw/2017/09/01/20170901_129.drs.fits.gz]
    --aux_dir=PATH              [default: /fact/aux/2017/09/01/]
    --out_dir=PATH              [default: /home/guest/relleums/qsub]
    --out_basename=PATH         [default: 20170901_139]
    --tmp_dir_basename=NAME     [default: phs_obs_]
"""
import docopt
import os
from glob import glob
from os.path import join
import subprocess
import tempfile
import shutil


def run(
    java_path,
    fact_tools_jar_path,
    fact_tools_xml_path,
    raw_path,
    drs_path,
    aux_dir,
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
            '-Dinfile=file:'+raw_path,
            '-Ddrsfile=file:'+drs_path,
            '-Daux_dir=file:'+aux_dir,
            '-Dout_path_basename=file:'+join(tmp, out_basename),
        ])

        for intermediate_file_path in glob(join(tmp, '*')):
            if os.path.isfile(intermediate_file_path):
                os.makedirs(out_dir, exist_ok=True, mode=0o755)
                shutil.copy(intermediate_file_path, out_dir)


def main():
    try:
        arguments = docopt.docopt(__doc__)

        run(
            java_path=arguments['--java_path'],
            fact_tools_jar_path=arguments['--fact_tools_jar_path'],
            fact_tools_xml_path=arguments['--fact_tools_xml_path'],
            raw_path=arguments['--raw_path'],
            drs_path=arguments['--drs_path'],
            aux_dir=arguments['--aux_dir'],
            out_dir=arguments['--out_dir'],
            out_basename=arguments['--out_basename'],
            tmp_dir_basename=arguments['--tmp_dir_basename'],
        )

    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()
