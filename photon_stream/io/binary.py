import numpy as np
from ..PhotonStream import PhotonStream
from ..Event import Event
from ..ObservationInformation import ObservationInformation
from ..simulation_truth import SimulationTruth
from . import magic_constants as magic
from array import array
import datetime as dt
import os
import gzip

LINEBREAK = np.array([np.iinfo(np.uint8).max], dtype=np.uint8)
OBSERVATION_TYPE_KEY = 0
SIMULATION_TYPE_KEY = 1

MAGIC_DESCRIPTOR_1 = ord('p')
MAGIC_DESCRIPTOR_2 = ord('h')
MAGIC_DESCRIPTOR_3 = ord('s')


def append_header_to_file(
    fout,
    event_type=OBSERVATION_TYPE_KEY, 
    pass_version=4
):  
    fout.write(np.uint8(MAGIC_DESCRIPTOR_1).tobytes())
    fout.write(np.uint8(MAGIC_DESCRIPTOR_2).tobytes())
    fout.write(np.uint8(MAGIC_DESCRIPTOR_3).tobytes())
    fout.write(np.uint8(pass_version).tobytes())
    fout.write(np.uint8(event_type).tobytes())


def read_header_from_file(fin):
    raw_header = np.fromstring(fin.read(5), dtype=np.uint8, count=5)
    return {
        'magic_1': raw_header[0],
        'magic_2': raw_header[1],
        'magic_3': raw_header[2],
        'pass_version': raw_header[3],
        'event_type': raw_header[4],
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


def append_observation_id_to_file(observation_info, fout):
    fout.write(observation_info.night.tobytes())
    fout.write(observation_info.run.tobytes())
    fout.write(observation_info.event.tobytes())


def read_observation_id_from_file(observation_info, fin):
    raw_id = np.fromstring(
        fin.read(12), 
        dtype=np.uint32, 
        count=3
    )
    observation_info.night = raw_id[0]
    observation_info.run = raw_id[1]
    observation_info.event = raw_id[2]


def append_observation_info_to_file(observation_info, fout):
    fout.write(observation_info._time_unix_s.tobytes())
    fout.write(observation_info._time_unix_us.tobytes())
    fout.write(observation_info.trigger_type.tobytes())


def read_observation_info_from_file(observation_info, fin):
    raw_info = np.fromstring(
        fin.read(12), 
        dtype=np.uint32, 
        count=3
    )
    observation_info.set_time_unix(
        time_unix_s=raw_info[0], 
        time_unix_us=raw_info[1],
    )
    observation_info.trigger_type = raw_info[2]


def append_pointing_to_file(event, fout):
    fout.write(event.zd.tobytes())
    fout.write(event.az.tobytes())


def read_pointing_from_file(event, fout):
    raw_pointing= np.fromstring(
        fout.read(8), 
        dtype=np.float32, 
        count=2
    )
    event.zd = raw_pointing[0]
    event.az = raw_pointing[1]


def append_photonstream_to_file(phs, fout):

    # Write number of pixels plus number of photons
    number_of_pixels_and_photons = len(phs.time_lines) + phs.number_photons
    fout.write(np.uint32(number_of_pixels_and_photons).tobytes())

    # WRITE PHOTON ARRIVAL SLICES
    raw_time_lines = np.zeros(
        number_of_pixels_and_photons, 
        dtype=np.uint8
    )
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
    phs.slice_duration = np.float32(magic.TIME_SLICE_DURATION_S)

    # read number of pixels and time lines
    number_of_pixels_and_photons = np.fromstring(
        fin.read(4),
        dtype=np.uint32,
        count=1
    )[0]

    # read photon-stream
    raw_time_lines = np.fromstring(
        fin.read(number_of_pixels_and_photons),
        dtype=np.uint8
    )

    """
    The following conversion is the dominant limit for the event rate during 
    reading.
    Without: 9430Hz
    With: 118Hz
    """

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
        count=1
    )[0]

    # READ saturated pixel CHIDs
    saturated_pixels_raw = np.fromstring(
        fin.read(number_of_pixels*2),
        dtype=np.uint16
    )
    return saturated_pixels_raw


def append_event_to_file(event, fout):
    if hasattr(event, 'observation_info'):
        append_header_to_file(fout, event_type=OBSERVATION_TYPE_KEY)
        append_observation_id_to_file(event.observation_info, fout)
        append_observation_info_to_file(event.observation_info, fout)
    elif hasattr(event, 'simulation_truth'):
        append_header_to_file(fout, event_type=SIMULATION_TYPE_KEY)
        append_simulation_id_to_file(event.simulation_truth, fout)
    else:
        raise
    append_pointing_to_file(event, fout)
    append_photonstream_to_file(event.photon_stream, fout)
    append_saturated_pixels_to_file(event.photon_stream.saturated_pixels, fout)


def read_event_from_file(fin):
    try:
        header = read_header_from_file(fin)
        event = Event()
        if header['event_type'] == OBSERVATION_TYPE_KEY:
            obs = ObservationInformation()
            read_observation_id_from_file(obs, fin)
            read_observation_info_from_file(obs, fin)
            event.observation_info = obs
        elif header['event_type'] == SIMULATION_TYPE_KEY:
            sim = SimulationTruth()
            read_simulation_id_from_file(sim, fin)
            event.simulation_truth = sim
        else:
            raise
        read_pointing_from_file(event, fin)
        event.photon_stream = read_photonstream_from_file(fin)  
        event.photon_stream.saturated_pixels = read_saturated_pixels_from_file(fin)
        return event
    except:
        raise StopIteration


def is_phs_binary(fin):
    h = read_header_from_file(fin)
    return (
        h['magic_1'] == ord('p') and
        h['magic_2'] == ord('h') and
        h['magic_3'] == ord('s') and
        h['pass_version'] == 4
    )


class Reader(object):
    def __init__(self, fin):
        self.fin = fin

    def __iter__(self):
        return self

    def __next__(self):
        return read_event_from_file(self.fin)

    def __repr__(self):
        out = '{}('.format(self.__class__.__name__)
        out += ')\n'
        return out