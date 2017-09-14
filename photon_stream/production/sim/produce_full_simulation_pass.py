import os
from glob import glob
from os.path import join
import shutil
from ..isdc import qsub
from shutil import which
from multiprocessing import Pool
from .produce_single_simulation_run import produce_single_simulation_run


RUN_NUMBER_DIGITS = 5


def produce_full_simulation_pass(
    ceres_dir,
    corsika_dir,
    out_dir,
):

    all_corsika = glob(join(corsika_dir,'*'))
    all_ceres = glob(join(ceres_dir,'*'))

    args = []
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
            args.append(
                (cer_sub_path, corsika_path, out_dir)
            )   
    
        except:
            pass

    with Pool(8) as p:
        return_codes = p.map(produce_single_simulation_run_wrapper, args)


def produce_single_simulation_run_wrapper(args):
    return produce_single_simulation_run(*args)
