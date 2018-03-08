"""
Usage: extract_muons -i=INPUT_PHS_DIRECTORY -o=OUTPUT_DIRECTORY

Options:
    -i --input_phs_dir=INPUT_PHS_DIRECTORY
    -o --out_dir=OUTPUT_DIRECTORY
"""
import docopt
import scoop
import os
import glob
import photon_stream as ps
from os.path import join
from os.path import split
from os.path import exists


def extract_single_run(cfg):
    os.makedirs(cfg['output_dir'], exist_ok=True, mode=0o755)
    output_run_path = join(
        cfg['output_dir'], cfg['output_base']+'_muons.phs.jsonl.gz')
    output_run_header_path = join(
        cfg['output_dir'], cfg['output_base']+'_muons.info')

    if exists(output_run_path) and exists(output_run_header_path):
        print('Already done', cfg['input_run_path'])
        return 0

    ps.muons.extraction.extract_muons_from_run(
        input_run_path=cfg['input_run_path'],
        output_run_path=output_run_path,
        output_run_header_path=output_run_header_path)
    print('Done', cfg['input_run_path'])
    return 0

if __name__ == '__main__':
    try:
        arguments = docopt.docopt(__doc__)

        phs_dir = arguments['--input_phs_dir']
        out_dir = arguments['--out_dir']
        run_paths = glob.glob(join(phs_dir, '2014/01/**/*.phs.jsonl.gz'))

        instructions = []
        for run_path in run_paths:

            year =  split(split(split(split(run_path)[0])[0])[0])[1]
            month = split(split(split(run_path)[0])[0])[1]
            night = split(split(run_path)[0])[1]
            base =  split(run_path)[1].split('.')[0]

            cfg = {
                'input_run_path': run_path,
                'output_dir': join(out_dir, year, month, night),
                'output_base': base,
            }
            instructions.append(cfg)

        return_codes = list(scoop.futures.map(
            extract_single_run,
            instructions))

    except docopt.DocoptExit as e:
        print(e)
