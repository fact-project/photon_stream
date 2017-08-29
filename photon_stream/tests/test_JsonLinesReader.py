import photon_stream as ps
import tempfile
import os
import pkg_resources
import gzip
import shutil

phs_jsonl_gz_path = pkg_resources.resource_filename(
    'photon_stream', 
    'tests/resources/20170119_229_pass4_100events.phs.jsonl.gz'
)


def do_gunzip(inpath, outpath):
    with gzip.open(inpath, 'rb') as f_in, open(outpath, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)    


def assert_phs_file_is_equal_to_std_jsonl_gz_file(path):
    gz_event_list = ps.EventListReader(phs_jsonl_gz_path)
    event_list = ps.EventListReader(path)
    for i, gz_event in enumerate(gz_event_list):
        print(i)
        event = next(event_list)
        assert gz_event == event


def test_reading_phs_jsonl():
    with tempfile.TemporaryDirectory(prefix='phs_') as tmp:
        path = os.path.join(tmp, 'run.phs.jsonl')
        do_gunzip(phs_jsonl_gz_path, path)
        assert_phs_file_is_equal_to_std_jsonl_gz_file(path)

def test_reading_phs_jsonl_gz():
    with tempfile.TemporaryDirectory(prefix='phs_') as tmp:
        path = phs_jsonl_gz_path
        assert_phs_file_is_equal_to_std_jsonl_gz_file(path)

def test_reading_phs():
    with tempfile.TemporaryDirectory(prefix='phs_') as tmp:
        path = os.path.join(tmp, 'run.phs')
        ps.jsonl2binary(phs_jsonl_gz_path, path+'.gz')
        do_gunzip(path+'.gz', path)
        assert_phs_file_is_equal_to_std_jsonl_gz_file(path)

def test_reading_phs_gz():
    with tempfile.TemporaryDirectory(prefix='phs_') as tmp:
        path = os.path.join(tmp, 'run.phs.gz')
        ps.jsonl2binary(phs_jsonl_gz_path, path)
        assert_phs_file_is_equal_to_std_jsonl_gz_file(path)