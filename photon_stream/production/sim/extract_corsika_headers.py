import gzip
from ...simulation_truth.corsika_headers import read_corsika_headers_from_file
from ...simulation_truth.corsika_headers import append_corsika_headers_to_file
from ...io import is_gzipped_file


def extract_corsika_headers(
    corsika_run_path,
    corsika_run_header_path
):
    if is_gzipped_file(corsika_run_path):
        with gzip.open(corsika_run_path, 'rb') as fin:
            headers = read_corsika_headers_from_file(fin)
    else:
        with open(corsika_run_path, 'rb') as fin:
            headers = read_corsika_headers_from_file(fin)

    if '.gz' in corsika_run_header_path:
        with gzip.open(corsika_run_header_path, 'wb') as fout:
            append_corsika_headers_to_file(headers=headers, fout=fout)
    else:
        with open(corsika_run_header_path, 'wb') as fout:
            append_corsika_headers_to_file(headers=headers, fout=fout)

