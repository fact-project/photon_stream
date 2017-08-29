from .JsonLinesReader import JsonLinesReader
from ..Event import Event
from . import binary
import shutil
import gzip


def jsonl2binary(input_path, output_path):
    run_in = JsonLinesReader(input_path)
    tmp_out_path = output_path+'.part'

    with gzip.open(tmp_out_path, 'wb') as fout:
        for event_dict in run_in:
            event = Event.from_event_dict(event_dict)
            binary.append_event_to_file(event, fout)
    shutil.move(tmp_out_path, output_path)