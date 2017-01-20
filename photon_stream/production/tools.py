import os
import stat
import subprocess


job_run_template = {
    'stdout_path': './stdout.txt',
    'stderr_path': './stderr.txt',
    'worker_node_script_path': './worker_node_script_path'
}


def submit_qsub_job(
    job_run=job_run_template, 
    queu='fact_medium', 
    email='sebmuell@phys.ethz.ch',
    print_only=True):

    cmd = [ 'qsub ',
            '-q', queu,
            '-o', job_run['stdout_path'],
            '-e', job_run['stderr_path'],
            '-m', 'ae', # send email in case of (e)nd or (a)bort
            '-M', email,
            job_run['worker_node_script_path']]
   
    if print_only:
        print(cmd)
    else:
        sp.check_output(cmd)


def write_worker_script(
    path,
    java_path,
    fact_tools_jar_path,
    fact_tools_xml_path,
    in_run_path,
    drs_path,
    aux_dir,
    out_dir,
    out_base_name):
    """
    Writes an executable bash script for a worker node to process one fact 
    raw date run into a photon-stream run. The intermediate output is stroed to 
    the workers /tmp and only moved to the output directory in the end.
    Jsonl status dicts are inserted at the begin and end of the std out 
    including timestamps.
    """

    sh = ''
    sh += '#!/bin/bash\n'
    sh += '\n'
    sh += '# FACT Telescope\n'
    sh += '# --------------\n'
    sh += '#\n'
    sh += '# Production of the compact photon-stream files from raw data.\n'
    sh += '# https://github.com/fact-project/photon_stream\n'
    sh += '# Sebastian A. Mueller, sebmuell@phys.ethz.ch\n'
    sh += '\n'
    sh += 'START_TIME=`date -Is`\n'
    sh += 'echo "{'
    sh +=         '\"JOB_ID\": \"$JOB_ID\", '
    sh +=         '\"JOB_NAME\": \"$JOB_NAME\", '
    sh +=         '\"START_TIME\": \"$START_TIME\", '
    sh +=         '\"HOSTNAME\": \"$HOSTNAME\", '
    sh +=         '\"USER\": \"$USER\"}"\n'
    sh += '\n'
    sh += 'export tmp_dir=/tmp/fact_photon_stream_JOB_ID_$JOB_ID\n'
    sh += 'mkdir -p $tmp_dir\n'
    sh += 'export PATH='+java_path+':$PATH\n' #/usr/java/jdk1.8.0_77/bin
    sh += '\n'
    sh += 'CALL="java \\\n'
    sh += '    -XX:MaxHeapSize=1024m \\\n'
    sh += '    -XX:InitialHeapSize=512m \\\n'
    sh += '    -XX:CompressedClassSpaceSize=64m \\\n'
    sh += '    -XX:MaxMetaspaceSize=128m \\\n'
    sh += '    -XX:+UseConcMarkSweepGC \\\n'
    sh += '    -XX:+UseParNewGC \\\n'
    sh += '    -jar '+fact_tools_jar_path+' \\\n'
    sh += '    '+fact_tools_xml_path+' \\\n'
    sh += '    -Dinfile='+in_run_path+' \\\n'
    sh += '    -Ddrsfile='+drs_path+' \\\n'
    sh += '    -DauxFolder='+aux_dir+' \\\n'
    sh += '    -Doutput=$tmp_dir/'+out_base_name+'" \\\n'
    sh += '\n'
    sh += 'echo $CALL\n'
    sh += 'eval $CALL\n'
    sh += '\n'
    sh += 'mkdir -p $out_dir\n'
    sh += 'cp $tmp_dir/* $out_dir/.\n'
    sh += 'rm -rf $tmp_dir\n'
    sh += '\n'
    sh += 'END_TIME=`date -Is`\n'
    sh += 'echo "{'
    sh +=         '\"JOB_ID\": \"$JOB_ID\", '
    sh +=         '\"JOB_NAME\": \"$JOB_NAME\", '
    sh +=         '\"START_TIME\": \"$START_TIME\", '
    sh +=         '\"END_TIME\": \"$END_TIME\"}"\n'
    
    with open(path, 'w') as fout:
        fout.write(sh)

    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)