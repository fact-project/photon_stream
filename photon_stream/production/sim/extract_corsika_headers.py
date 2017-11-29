import gzip
from ...simulation_truth.corsika_headers import read_corsika_headers_from_file
from ...simulation_truth.corsika_headers import append_corsika_headers_to_file
from ...io import is_gzipped_file
import shutil


def extract_corsika_headers(
    in_path,
    out_path
):
    """
    Reads a MMCS CORSIKA 'cer' file from in_path and extracts al headers:
    run header, event header, and run end header (if present)
    Then writes only the headers back into the out_path.

    Parameters
    ----------
    in_path=PATH    Input MMCS CORSIKA run path with (or without) the Cherenkov
                    photon blocks.

    out_path=PATH   Output path to the new header only MMCS CORSIKA run without
                    the Cherenkov photon blocks.
    """
    if is_gzipped_file(in_path):
        with gzip.open(in_path, 'rb') as fin:
            headers = read_corsika_headers_from_file(fin)
    else:
        with open(in_path, 'rb') as fin:
            headers = read_corsika_headers_from_file(fin)

    tmp_out_path = out_path+'.part'

    if '.gz' in out_path:
        with gzip.open(tmp_out_path, 'wb') as fout:
            append_corsika_headers_to_file(headers=headers, fout=fout)
    else:
        with open(tmp_out_path, 'wb') as fout:
            append_corsika_headers_to_file(headers=headers, fout=fout)

    shutil.move(tmp_out_path, out_path)

