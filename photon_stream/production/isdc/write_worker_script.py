import os, stat

def write_worker_script(
    path,
    java_path='/usr/java/jdk1.8.0_77/bin',
    fact_tools_jar_path='/fact_tools.jar',
    fact_tools_xml_path='/fact_tools.xml',
    in_run_path='fact/raw/YYYY/mm/dd/YYYYmmdd_RRR.fits.fz',
    drs_path='fact/raw/YYYY/mm/dd/YYYYmmdd_RRR.drs.fits.gz',
    aux_dir='fact/aux/YYYY/mm/dd/',
    out_dir='/home/photon_stream/YYYY/mm/dd/',
    out_base_name='YYYYmmdd_RRR.phs.jsonl.gz',
    tmp_dir_base_name='fact_photon_stream_JOB_ID_'):
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
    sh += '# Dominik Neise, neised@phys.ethz.ch\n'
    sh += '\n'

    sh += 'START_TIME=`date -Is`\n'
    sh += 'echo "{'
    sh +=         '\\\"JOB_ID\\\": \\\"$JOB_ID\\\", '
    sh +=         '\\\"JOB_NAME\\\": \\\"$JOB_NAME\\\", '
    sh +=         '\\\"START_TIME\\\": \\\"$START_TIME\\\", '
    sh +=         '\\\"HOSTNAME\\\": \\\"$HOSTNAME\\\", '
    sh +=         '\\\"USER\\\": \\\"$USER\\\"}"\n'
    sh += '\n'

    sh += '# Create TMP_DIR for this run\n'
    sh += 'TMP_DIR=/tmp/'+tmp_dir_base_name+'$JOB_ID\n'
    sh += 'mkdir -p $TMP_DIR\n'
    sh += '\n'

    sh += '# Use a specific JAVA\n'
    sh += 'export PATH='+java_path+':$PATH\n'
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
    sh += '    -Dinfile=file:'+in_run_path+' \\\n'
    sh += '    -Ddrsfile=file:'+drs_path+' \\\n'
    sh += '    -Daux_dir=file:'+aux_dir+' \\\n'
    sh += '    -Dout_path_basename=file:$TMP_DIR/'+out_base_name+'" \\\n'
    sh += '\n'

    sh += 'echo $CALL\n'
    sh += 'eval $CALL\n'
    sh += '\n'

    sh += 'mkdir -p '+out_dir+'\n'
    sh += 'cp $TMP_DIR/* '+os.path.join(out_dir,'.')+'\n'
    sh += 'rm -rf $TMP_DIR\n'
    sh += '\n'

    sh += 'END_TIME=`date -Is`\n'
    sh += 'echo "{'
    sh +=         '\\\"JOB_ID\\\": \\\"$JOB_ID\\\", '
    sh +=         '\\\"JOB_NAME\\\": \\\"$JOB_NAME\\\", '
    sh +=         '\\\"START_TIME\\\": \\\"$START_TIME\\\", '
    sh +=         '\\\"END_TIME\\\": \\\"$END_TIME\\\", '
    sh +=         '\\\"HOSTNAME\\\": \\\"$HOSTNAME\\\", '
    sh +=         '\\\"USER\\\": \\\"$USER\\\", '
    sh +=         '\\\"FACT_TOOLS_JAR\\\": \\\"'+fact_tools_jar_path+'\\\", '
    sh +=         '\\\"FACT_TOOLS_XML\\\": \\\"'+fact_tools_xml_path+'\\\", '
    sh +=         '\\\"OBSERVATION\\\": \\\"'+in_run_path+'\\\", '
    sh +=         '\\\"DRS\\\": \\\"'+drs_path+'\\\", '
    sh +=         '\\\"AUX\\\": \\\"'+aux_dir+'\\\", '
    sh +=         '\\\"JAVA\\\": \\\"'+java_path+'\\\"}"\n'
    
    with open(path, 'w') as fout:
        fout.write(sh)

    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)