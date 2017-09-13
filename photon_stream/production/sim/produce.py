import os
from glob import glob
from os.path import join
import shutil
import photon_stream as ps

RUN_NUMBER_DIGITS = 5

def run(
    ceres_dir,
    corsika_dir,
    out_dir,
):

    all_corsika = glob(join(corsika_dir,'*'))
    all_ceres = glob(join(ceres_dir,'*'))

    for corsika_path in all_corsika:
        try:
            cor_basename = os.path.basename(corsika_path)
            assert 'cer' == cor_basename[0:3]
            run_number = int(cor_basename[3:3+RUN_NUMBER_DIGITS+1])

            run_number_str = str(run_number)
            for cer_path in all_ceres:
                if run_number_str in cer_path:
                    break
            
            all_in_cer_path = glob(join(cer_path,'*'))
            for cer_sub_path in all_in_cer_path:
                if 'Events.fits.gz' in cer_sub_path:
                    break   

            print(corsika_path, ' + ', cer_sub_path)
        except:
            pass



def process_sim_run(
    ceres_events_path, 
    corsika_path, 
    out_dir,
    fact_tools_jar_path='/net/big-tank/POOL/projects/fact/smueller/fact-tools/target/fact-tools-0.18.1.jar',
):
    ceres_basename = os.path.basename(ceres_events_path)
    corsika_basename = os.path.basename(corsika_path)

    ceres_run = int(ceres_basename.split('.')[0])
    corsika_run = int(cor_basename[3:3+RUN_NUMBER_DIGITS+1])

    assert ceres_run == corsika_run

    os.makedirs(out_dir, exist_ok=True, mode=0o755)

    corsika_header_path = '{5:d}.ch.gz'.format(ceres_run)
    phs_basename = '{5:d}'.format(ceres_run)

    corsika_header_path = join(out_dir, corsika_header_path)

    ps.production.sim.extract_corsika_headers(
        in_path=corsika_path,
        out_path=corsika_header_path
    )

    ps.production.sim.extract_single_photons(
        ceres_path=ceres_events_path,
        out_dir=out_dir,
        out_basename=phs_basename,
        fact_tools_jar_path=fact_tools_jar_path,
    )