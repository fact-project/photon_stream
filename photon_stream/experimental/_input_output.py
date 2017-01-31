import numpy as np
from ..PhotonStream import PhotonStream

linebreak = np.array([np.iinfo(np.uint8).max], dtype=np.uint8)

def append_photonstream_to_file(phs, fout):
    # WRITE NUMBER OF TIME LINES
    number_of_time_lines = len(phs.time_lines)
    fout.write(np.uint32(number_of_time_lines).tobytes())

    # WRITE NUMBER OF PHOTONS
    number_of_photons = phs.number_photons
    fout.write(np.uint32(number_of_photons).tobytes())

    # WRITE SLICE DURATION
    fout.write(np.float32(phs.slice_duration).tobytes())

    # WRITE PHOTON ARRIVAL SLICES
    raw_time_lines = np.zeros(
        number_of_photons+number_of_time_lines, 
        dtype=np.uint8)
    pos = 0
    for time_line in phs.time_lines:
        for photon_arrival in time_line:
            raw_time_lines[pos] = photon_arrival
            pos += 1
        raw_time_lines[pos] = linebreak
        pos += 1
    fout.write(raw_time_lines.tobytes())


def read_photonstream_from_file(fin):
    phs = PhotonStream()

    # READ NUMBER OF TIME LINES
    number_of_time_lines = np.fromfile(fin, dtype=np.uint32, count=1)[0]

    # READ NUMBER OF PHOTONS
    number_of_photons = np.fromfile(fin, dtype=np.uint32, count=1)[0]

    # READ SLICE DURATION
    slice_duration = np.fromfile(fin, dtype=np.float32, count=1)[0]
    phs.slice_duration = slice_duration

    # READ PHOTONSTREAM
    raw_time_lines = np.fromfile(
        fin, 
        dtype=np.uint8, 
        count=number_of_photons+number_of_time_lines)

    phs.time_lines = []
    for pixel in range(number_of_time_lines):
        empty_time_line = []
        phs.time_lines.append(empty_time_line)

    pixel = 0
    for symbol in raw_time_lines:
        if symbol == linebreak:
            pixel += 1
        else:
            phs.time_lines[pixel].append(symbol)
    return phs