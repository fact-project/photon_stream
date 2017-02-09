import numpy as np
from ..PhotonStream import PhotonStream
from ..Event import Event

linebreak = np.array([np.iinfo(np.uint8).max], dtype=np.uint8)

def append_photonstream_to_file(phs, fout):

    # WRITE SLICE DURATION
    fout.write(np.float32(phs.slice_duration).tobytes())

    # Write number of pixels plus number of photons
    number_of_pixels_and_photons = len(phs.time_lines) + phs.number_photons
    fout.write(np.uint32(number_of_pixels_and_photons).tobytes())

    # WRITE PHOTON ARRIVAL SLICES
    raw_time_lines = np.zeros(
        number_of_pixels_and_photons, 
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

    # read slice duration
    phs.slice_duration = np.fromstring(
        fin.read(4),
        dtype=np.float32,
        count=1)[0]

    # read number of pixels and time lines
    number_of_pixels_and_photons = np.fromstring(
        fin.read(4),
        dtype=np.uint32,
        count=1)[0]

    # read photon-stream
    raw_time_lines = np.fromstring(
        fin.read(number_of_pixels_and_photons),
        dtype=np.uint8)

    phs.time_lines = []
    if len(raw_time_lines) > 0:
        phs.time_lines.append([])

    pixel = 0
    for i, symbol in enumerate(raw_time_lines):
        if symbol == linebreak:
            pixel += 1
            if i+1 < len(raw_time_lines):
                phs.time_lines.append([])
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
    number_of_pixels = np.fromstring(
        fin.read(2),
        dtype=np.uint16,
        count=1)[0]

    # READ saturated pixel CHIDs
    saturated_pixels_raw = np.fromstring(
        fin.read(number_of_pixels*2),
        dtype=np.uint16)
    return saturated_pixels_raw


def append_event_to_file(event, fout):
    fout.write(np.uint32(event.night).tobytes())
    fout.write(np.uint32(event.run_id).tobytes())
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
    try:
        event = Event()
        header = np.fromstring(
            fin.read(24),
            dtype=np.uint32,
            count=6)
        event.night = header[0]
        event.run_id = header[1]
        event.id = header[2]
        event._time_unix_s = header[3]
        event._time_unix_us = header[4]
        event.trigger_type = header[5]
        pointing = np.fromstring(
            fin.read(8),
            dtype=np.float32,
            count=2)
        event.zd = pointing[0]
        event.az = pointing[1]
        event.photon_stream = read_photonstream_from_file(fin)
        event.saturated_pixels = read_saturated_pixels_from_file(fin)
        return event
    except:
        raise StopIteration