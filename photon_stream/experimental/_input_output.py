import numpy as np
from ..PhotonStream import PhotonStream
from ..Event import Event
from ..ObservationInformation import ObservationInformation
from array import array
import datetime as dt
import os
import gzip

LINEBREAK = np.array([np.iinfo(np.uint8).max], dtype=np.uint8)

def append_header_to_file(header, fout):
    fout.write(np.uint8(header['pass']).tobytes())
    if header['type'] == 'observation':
        event_type = np.uint8(0)
    elif header['type'] == 'simulation':
        event_type = np.uint8(1)
    else:
        raise
    fout.write(event_type.tobytes())
    fout.write(np.uint8(header['future_problems_0']).tobytes())
    fout.write(np.uint8(header['future_problems_1']).tobytes())


def read_header_from_file(fin):
    raw_header = np.fromstring(fin.read(4), dtype=np.uint8, count=4)
    if raw_header[1] == 0:
        type_str = 'observation'
    elif raw_header[1] == 1:
        type_str = 'simulation'
    else:
        raise
    return {
        'pass': raw_header[0],
        'type': type_str,
        'future_problems_0': raw_header[2],
        'future_problems_1': raw_header[3]
    }


def append_simulation_id_to_file(simulation_truth, fout):
    fout.write(simulation_truth.run.tobytes())
    fout.write(simulation_truth.event.tobytes())
    fout.write(simulation_truth.reuse.tobytes())


def read_simulation_id_from_file(simulation_truth, fin):
    raw_id = np.fromstring(
        fin.read(12), 
        dtype=np.uint32, 
        count=3
    )
    simulation_truth.run = raw_id[0]
    simulation_truth.event = raw_id[1]
    simulation_truth.reuse = raw_id[2]


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
        raw_time_lines[pos] = LINEBREAK
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
        phs.time_lines.append(array('B'))

    pixel = 0
    for i, symbol in enumerate(raw_time_lines):
        if symbol == LINEBREAK:
            pixel += 1
            if i+1 < len(raw_time_lines):
                phs.time_lines.append(array('B'))
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
    fout.write(np.uint32(event.observation_info.night).tobytes())
    fout.write(np.uint32(event.observation_info.run).tobytes())
    fout.write(np.uint32(event.observation_info.event).tobytes())
    # 12
    fout.write(np.uint32(event.observation_info._time_unix_s).tobytes())
    fout.write(np.uint32(event.observation_info._time_unix_us).tobytes())
    fout.write(np.uint32(event.observation_info.trigger_type).tobytes())
    # 24
    fout.write(np.float32(event.zd).tobytes())
    fout.write(np.float32(event.az).tobytes())
    # 32
    append_photonstream_to_file(event.photon_stream, fout)
    append_saturated_pixels_to_file(event.photon_stream.saturated_pixels, fout)


def read_event_from_file(fin):
    try:
        header = np.fromstring(
            fin.read(24),
            dtype=np.uint32,
            count=6
        )

        obs = ObservationInformation()
        obs.night = header[0]
        obs.run = header[1]
        obs.event = header[2]
        obs._time_unix_s = header[3]
        obs._time_unix_us = header[4]
        obs.time = dt.datetime.utcfromtimestamp(
            obs._time_unix_s + obs._time_unix_us / 1e6)
        obs.trigger_type = header[5]

        pointing = np.fromstring(
            fin.read(8),
            dtype=np.float32,
            count=2)

        event = Event()
        event.observation_info = obs
        event.zd = pointing[0]
        event.az = pointing[1]
        event.photon_stream = read_photonstream_from_file(fin)  
        event.photon_stream.saturated_pixels = read_saturated_pixels_from_file(fin)

        return event
    except:
        raise StopIteration


class Run(object):
    """
    Sequentially reads a gzipped binary run and provides events.
    """
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.file = gzip.open(path, "rb")

    def __exit__(self):
        self.file.close()

    def __iter__(self):
        return self

    def __next__(self):
        return read_event_from_file(self.file)

    def __repr__(self):
        out = 'BinaryRun('
        out += self.path+')\n'
        return out