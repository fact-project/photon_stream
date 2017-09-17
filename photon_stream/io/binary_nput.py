"""
Next Pixel symbol Used Twice (NPUT)

A more compact binary format
"""
from ..PhotonStream import PhotonStream
from . import magic_constants as magic
from array import array
import numpy as np


def append_nput_photonstream_to_file(phs, fout):
    num_empty_pixel = 0
    for time_line in phs.time_lines:
        if len(time_line) == 0:
            num_empty_pixel += 1
    num_photons_plus_num_empty_pixel = phs.number_photons + num_empty_pixel

    fout.write(np.uint32(num_photons_plus_num_empty_pixel).tobytes())
    fout.write(np.uint16(num_empty_pixel).tobytes())

    raw = np.zeros(num_photons_plus_num_empty_pixel, dtype=np.uint8)
    
    pos = 0
    for time_line in phs.time_lines:
        if len(time_line) == 0:
            raw[pos] = 200
            pos += 1
        else:
            for i, arr_time in enumerate(time_line):
                rel_arr_time = arr_time - magic.NUMBER_OF_TIME_SLICES_OFFSET_AFTER_BEGIN_OF_ROI

                if i+1 == len(time_line):
                    # last photon in time line
                    raw[pos] = rel_arr_time + 100
                    pos += 1
                else:
                    raw[pos] = rel_arr_time
                    pos += 1     
    fout.write(raw.tobytes())


def read_nput_photonstream_from_file(fin):
    phs = PhotonStream()
    phs.slice_duration = np.float32(magic.TIME_SLICE_DURATION_S)

    num_photons_plus_num_empty_pixel = np.fromstring(
        fin.read(4),
        dtype=np.uint32,
        count=1
    )[0]

    num_empty_pixel = np.fromstring(
        fin.read(2),
        dtype=np.uint16,
        count=1
    )[0]

    num_photons = num_photons_plus_num_empty_pixel - num_empty_pixel

    raw = np.fromstring(
        fin.read(num_photons_plus_num_empty_pixel),
        dtype=np.uint8
    )

    phs.time_lines = []
    for pixel in range(magic.NUMBER_OF_PIXELS):
        phs.time_lines.append(array('B'))

    pixel = 0
    for symbol in raw:
        if symbol >= 200:
            pixel += 1
        elif symbol >= 100:
            rel_arr_time = symbol - 100
            arr_time = rel_arr_time + magic.NUMBER_OF_TIME_SLICES_OFFSET_AFTER_BEGIN_OF_ROI
            phs.time_lines[pixel].append(arr_time)
            pixel += 1
        else:
            rel_arr_time = symbol
            arr_time = rel_arr_time + magic.NUMBER_OF_TIME_SLICES_OFFSET_AFTER_BEGIN_OF_ROI
            phs.time_lines[pixel].append(arr_time)
    return phs