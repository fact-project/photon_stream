import os

def make_worker_script(
    fact_tools_jar_path,
    fact_tools_xml_path,
    in_run_path,
    drs_path,
    aux_dir,
    out_dir,
    out_base_name):

    sh = ''
    sh += '#!/bin/bash\n'
    sh += '\n'
    sh += 'START_TIME=`date -Is`\n'
    sh += 'echo "{ \"JOB_ID\": \"$JOB_ID\", \"JOB_NAME\": \"$JOB_NAME\", \"START_TIME\": \"$START_TIME\", \"HOSTNAME\": \"$HOSTNAME\", \"USER\": \"$USER\"}"\n'
    sh += '\n'
    sh += 'export tmp_dir=/tmp/fact_photon_stream_JOB_ID_$JOB_ID\n'
    sh += 'mkdir -p $tmp_dir\n'
    sh += 'export PATH=/usr/java/jdk1.8.0_77/bin:$PATH\n'
    sh += '\n'
    sh += 'java \\\n'
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
    sh += '    -Doutput=$tmp_dir/'+out_base_name+' \\\n'
    sh += '\n'
    sh += 'mkdir -p $out_dir\n'
    sh += 'cp $tmp_dir/* $out_dir/.\n'
    sh += 'rm -rf $tmp_dir\n'
    sh += '\n'
    sh += 'END_TIME=`date -Is`\n'
    sh += 'echo "{ \"JOB_ID\": \"$JOB_ID\", \"JOB_NAME\": \"$JOB_NAME\", \"START_TIME\": \"$START_TIME\", \"END_TIME\": \"$END_TIME\"}"\n'
    return sh