import numpy as np
import photon_stream as ps
import pkg_resources
import tempfile
import gzip
import json
import os

"""
According to http://jsonlines.org/:

'The last character in the file may be a line separator, 
and it will be treated the same as if there was no line separator present.'

But 'may' is not 'must'.
"""


def test_jsonl_event_counter_empty():
    with tempfile.TemporaryDirectory(prefix='phs_test_status_') as tmp:
        f = os.path.join(tmp, 'empty.jsonl.gz')
        with gzip.open(f, 'wt') as fout:
            pass
        assert ps.production.status.number_of_events_in_run(f) == 0


def test_jsonl_event_counter_only_newline():
    with tempfile.TemporaryDirectory(prefix='phs_test_status_') as tmp:
        f = os.path.join(tmp, 'only_newline.jsonl.gz')
        with gzip.open(f, 'wt') as fout:
            fout.write('\n')
        assert ps.production.status.number_of_events_in_run(f) == 1


def test_jsonl_event_counter_one_event_no_newline():
    with tempfile.TemporaryDirectory(prefix='phs_test_status_') as tmp:
        f = os.path.join(tmp, 'one_event_no_newline.jsonl.gz')
        with gzip.open(f, 'wt') as fout:
            json.dump('{"Comment":"I am a dummy"}', fout)
        assert ps.production.status.number_of_events_in_run(f) == 0


def test_jsonl_event_counter_one_event_with_newline():
    with tempfile.TemporaryDirectory(prefix='phs_test_status_') as tmp:
        f = os.path.join(tmp, 'one_event_with_newline.jsonl.gz')
        with gzip.open(f, 'wt') as fout:
            json.dump('{"Comment":"I am a dummy"}', fout)
            fout.write('\n')
        assert ps.production.status.number_of_events_in_run(f) == 1


def test_jsonl_event_counter_three_events_with_three_newline():
    with tempfile.TemporaryDirectory(prefix='phs_test_status_') as tmp:
        f = os.path.join(tmp, 'three_events_with_three_newline.jsonl.gz')
        with gzip.open(f, 'wt') as fout:
            json.dump('{"Comment":"I am a dummy"}', fout)
            fout.write('\n')
            json.dump('{"Comment":"I am a dummy"}', fout)
            fout.write('\n')
            json.dump('{"Comment":"I am a dummy"}', fout)
            fout.write('\n')
        assert ps.production.status.number_of_events_in_run(f) == 3


def test_jsonl_event_counter_three_events_with_two_newline():
    with tempfile.TemporaryDirectory(prefix='phs_test_status_') as tmp:
        f = os.path.join(tmp, 'three_events_with_two_newline.jsonl.gz')
        with gzip.open(f, 'wt') as fout:
            json.dump('{"Comment":"I am a dummy"}', fout)
            fout.write('\n')
            json.dump('{"Comment":"I am a dummy"}', fout)
            fout.write('\n')
            json.dump('{"Comment":"I am a dummy"}', fout)
        assert ps.production.status.number_of_events_in_run(f) == 2