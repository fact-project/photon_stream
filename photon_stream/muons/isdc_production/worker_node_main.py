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
import shutil
import tempfile
from ..extraction import extract_muons_from_run
import datetime as dt
from os.path import join
from os.path import split


class TimeDeltaInfo(object):
    def __init__(self):
        self.last = None

    def info(self, text):
        if self.last is None:
            self.last = dt.datetime.now()
            return '['+self.last.isoformat()+'] '+text
        else:
            now = dt.datetime.now()
            delta = now - self.last
            delta_seconds = (
                float(delta.seconds) +
                float(delta.microseconds)/1e6
            )
            info = '['+now.isoformat()+' + '+str(delta_seconds)+'s] '+text
            self.last = now
            return info


def main():
    try:
        tdi = TimeDeltaInfo()
        print(tdi.info('Start muon extraction.'))

        arguments = docopt.docopt(__doc__)

        input_run_path = arguments['--input_run_path']
        out_path = arguments['--out_path']

        out_muon_run_path = out_path + '_muons.phs.jsonl.gz'
        out_muon_run_info_path = out_path + '_muons.info'

        out_dir = split(out_path)[0]
        if out_dir:
            os.makedirs(out_dir, exist_ok=True, mode=0o755)
            print(tdi.info('Output directory was created.'))

        with tempfile.TemporaryDirectory(prefix='relleums_fact_') as tmp:
            print(tdi.info("Temp. dir was created on worker node: '"+tmp+"'"))

            input_run_base = split(input_run_path)[1]
            tmp_input_run_path = join(tmp, input_run_base)

            shutil.copy(input_run_path, tmp_input_run_path)

            tmp_out_muon_run_path = join(
                tmp,
                input_run_base + '_muons.phs.jsonl.gz')
            tmp_out_muon_run_info_path = join(
                tmp,
                input_run_base + '_muons.info')

            print(tdi.info('Input run was copied to worker node temp. dir.'))

            extract_muons_from_run(
                input_run_path=tmp_input_run_path,
                output_run_path=tmp_out_muon_run_path,
                output_run_header_path=tmp_out_muon_run_info_path)

            print(tdi.info('Muons have been extracted.'))

            shutil.copy(tmp_out_muon_run_path, out_muon_run_path)
            shutil.copy(tmp_out_muon_run_info_path, out_muon_run_info_path)

            print(tdi.info('Done. Output has been moved to permanent storage'))

    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()
