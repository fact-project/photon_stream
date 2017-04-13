"""
Usage: phs_extract_muons -i=INPUT_RUN_PATH -o=OUT_PATH

Options:
    -i --input_run_path=INPUT_RUN_PATH
    -o --out_path=OUT_PATH

Extracts muon events from the FACT photon stream. Writes two output files.
    
    1) A run of only muon like events.
        out_path + '_muons.phs.jsonl.gz'

    2) A binary info table with muon properties for each event.
        out_path + '_muons.info'

The output directories are created on the fly if not existing.
"""
import docopt
import os
from ..extraction import extract_muons_from_run

def main():
    try:
        
        arguments = docopt.docopt(__doc__)

        input_run_path = arguments['--input_run_path']
        out_path = arguments['--out_path']

        out_muon_run_path = out_path + '_muons.phs.jsonl.gz'
        out_muon_run_info_path = out_path + '_muons.info'

        out_dir = os.path.split(out_path)[0]
        os.makedirs(out_dir, exist_ok=True)
        
        extract_muons_from_run(
            input_run_path=input_run_path, 
            output_run_path=out_muon_run_path, 
            output_run_header_path=out_muon_run_info_path)

    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()