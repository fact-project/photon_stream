import photon_stream as ps
import tempfile
import os
import pkg_resources
import gzip
import shutil


def gunzip(inpath, outpath):
    with gzip.open(inpath, 'rb') as f_in, open(outpath, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)    


def test_reading_gzipped_and_non_gzipped_files():
    gz_path = pkg_resources.resource_filename(
        'photon_stream', 
        'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz'
    )

    with tempfile.TemporaryDirectory(prefix='phs_JsonLinesReader_') as tmp:
        path = os.path.join(tmp, '20170119_229_pass4_100events.phs.jsonl')

        gunzip(gz_path, path)

        gz_event_list = ps.EventListReader(gz_path)
        event_list = ps.EventListReader(path)

        for i, gz_event in enumerate(gz_event_list):
            print(i)
            event = next(event_list)
            assert gz_event == event
