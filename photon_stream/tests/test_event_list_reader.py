import photon_stream as ps
import tempfile
import os
import pkg_resources
import gzip
import shutil


phs_jsonl_gz_paths = [
    pkg_resources.resource_filename(
        'photon_stream',
        os.path.join(
            'tests',
            'resources',
            '20170119_229_pass4_100events.phs.jsonl.gz'
        )
    ),
    pkg_resources.resource_filename(
        'photon_stream',
        os.path.join('tests', 'resources', '011014.phs.jsonl.gz')
    )
]


def do_gunzip(inpath, outpath):
    with gzip.open(inpath, 'rb') as f_in, open(outpath, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


def assert_event_lists_in_files_are_equal(path1, path2):
    gz_event_list = ps.EventListReader(path1)
    event_list = ps.EventListReader(path2)
    for i, gz_event in enumerate(gz_event_list):
        print(i)
        event = next(event_list)
        assert gz_event == event


def test_reading_phs_jsonl():
    for run_path in phs_jsonl_gz_paths:
        with tempfile.TemporaryDirectory(prefix='phs_') as tmp:
            path = os.path.join(tmp, 'run.phs.jsonl')
            do_gunzip(run_path, path)
            assert_event_lists_in_files_are_equal(run_path, path)

def test_reading_phs_jsonl_gz():
    for run_path in phs_jsonl_gz_paths:
        with tempfile.TemporaryDirectory(prefix='phs_') as tmp:
            path = run_path
            assert_event_lists_in_files_are_equal(run_path, path)

def test_reading_phs():
    for run_path in phs_jsonl_gz_paths:
        with tempfile.TemporaryDirectory(prefix='phs_') as tmp:
            path = os.path.join(tmp, 'run.phs')
            ps.jsonl2binary(run_path, path+'.gz')
            do_gunzip(path+'.gz', path)
            assert_event_lists_in_files_are_equal(run_path, path)

def test_reading_phs_gz():
    for run_path in phs_jsonl_gz_paths:
        with tempfile.TemporaryDirectory(prefix='phs_') as tmp:
            path = os.path.join(tmp, 'run.phs.gz')
            ps.jsonl2binary(run_path, path)
            assert_event_lists_in_files_are_equal(run_path, path)
