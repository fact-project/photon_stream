import numpy as np
from ..PhotonStream import PhotonStream
from ..Event import Event
from ..ObservationInformation import ObservationInformation
import datetime as dt
import os
import gzip

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

    where = np.where(raw_time_lines == linebreak)[0][:-1] + 1
    phs.time_lines = [
        part[:-1]
        for part in np.split(raw_time_lines, where)
    ]
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
        event.photon_stream.saturated_pixels = (
            read_saturated_pixels_from_file(fin))

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
