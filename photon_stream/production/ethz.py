from .make_job_list import make_job_list
from .make_job_list import FACT_TOOLS_OBSERVATIONS_STEERING_CARD_PATH
from .write_worker_script import write_worker_script


def ethz(
    out_dir, 
    start_night=20150101, 
    end_night=20150102,
    only_a_fraction=1.0,
    fact_raw_dir='/data/fact_data',
    fact_drs_dir='/data/fact_drs.fits',
    fact_aux_dir='/data/fact_aux',
    java_path='/home/relleums/java8/jdk1.8.0_111',
    fact_tools_jar_path='/home/relleums/fact-tools/target/fact-tools-0.18.0.jar',
    fact_tools_xml_path=FACT_TOOLS_OBSERVATIONS_STEERING_CARD_PATH,
    tmp_dir_base_name='fact_photon_stream_JOB_ID_',
    runinfo=None,
    only_append=True,
    scoop_hosts='/home/relleums/scoop_hosts.txt'
):
    jobs = make_job_list(
        out_dir=out_dir,
        start_night=start_night,
        end_night=end_night,
        only_a_fraction=only_a_fraction,
        fact_raw_dir=fact_raw_dir,
        fact_drs_dir=fact_drs_dir,
        fact_aux_dir=fact_aux_dir,
        java_path=java_path,
        fact_tools_jar_path=fact_tools_jar_path,
        fact_tools_xml_path=fact_tools_xml_path,
        tmp_dir_base_name=tmp_dir_base_name,
        runinfo=runinfo,
        only_append=only_append,
    )