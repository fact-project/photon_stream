import numpy as np
from ..PhotonStream import PhotonStream
from ..Event import Event

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



def append_saturated_pixels_to_file(saturated_pixels, fout):
    # WRITE NUMBER OF PIXELS
    number_of_pixels = len(saturated_pixels)
    fout.write(np.uint16(number_of_pixels).tobytes())

    saturated_pixels_raw = np.array(saturated_pixels, dtype=np.uint16)
    fout.write(saturated_pixels_raw.tobytes())


def read_saturated_pixels_from_file(fin):
    # READ NUMBER OF PIXELS
    number_of_pixels = np.fromfile(fin, dtype=np.uint16, count=1)[0]

    # READ PHOTONSTREAM
    saturated_pixels_raw = np.fromfile(
        fin, 
        dtype=np.uint16, 
        count=number_of_pixels)
    return saturated_pixels_raw.tolist()


def append_event_to_file(event, fout):
    fout.write(np.uint32(event.run.night).tobytes())
    fout.write(np.uint32(event.run.id).tobytes())
    fout.write(np.uint32(event.id).tobytes())
    # 12
    fout.write(np.uint32(event._time_unix_s).tobytes())
    fout.write(np.uint32(event._time_unix_us).tobytes())
    fout.write(np.uint32(event.trigger_type).tobytes())
    # 24
    fout.write(np.float32(event.zd).tobytes())
    fout.write(np.float32(event.az).tobytes())
    # 32
    append_photonstream_to_file(event.photon_stream, fout)
    append_saturated_pixels_to_file(event.saturated_pixels, fout)


def read_event_from_file(fin):
    event = Event()
    header = np.fromfile(fin, dtype=np.uint32, count=6)
    event.night = header[0]
    event.run_id = header[1]
    event.id = header[2]
    event._time_unix_s = header[3]
    event._time_unix_us = header[4]
    event.trigger_type = header[5]
    pointing = np.fromfile(fin, dtype=np.float32, count=2)
    event.zd = pointing[0]
    event.az = pointing[1]
    event.photon_stream = read_photonstream_from_file(fin)
    event.saturated_pixels = read_saturated_pixels_from_file(fin)
    return event