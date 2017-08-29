from .EventListReader import EventListReader
from .Event import Event
from .io import binary
import shutil
import gzip


def jsonl2binary(input_path, output_path):
    run_in = EventListReader(input_path)
    tmp_out_path = output_path+'.part'
    with gzip.open(tmp_out_path, 'wb') as fout:
        for event in run_in:
            binary.append_event_to_file(event, fout)
    shutil.move(tmp_out_path, output_path)