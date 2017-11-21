from ..photon_stream import PhotonStream
from ..event import Event
from ..observation_information import ObservationInformation
from ..simulation_truth import SimulationTruth
from . import magic_constants as magic
from array import array
import numpy as np

LINEBREAK = np.uint8(np.iinfo(np.uint8).max)
OBSERVATION_EVENT_TYPE_KEY = 0
SIMULATION_EVENT_TYPE_KEY = 1

MAGIC_DESCRIPTOR_1 = ord('p')
MAGIC_DESCRIPTOR_2 = ord('h')
MAGIC_DESCRIPTOR_3 = ord('s')


class Descriptor():
    def __init__(self):
        self.magic_1 = MAGIC_DESCRIPTOR_1
        self.magic_2 = MAGIC_DESCRIPTOR_2
        self.magic_3 = MAGIC_DESCRIPTOR_3
        self.pass_version = magic.SINGLEPULSE_EXTRACTOR_PASS
        self.event_type = OBSERVATION_EVENT_TYPE_KEY

    def is_valid(self):
        return (
            self.magic_1 == MAGIC_DESCRIPTOR_1 and
            self.magic_2 == MAGIC_DESCRIPTOR_2 and
            self.magic_3 == MAGIC_DESCRIPTOR_3 and
            self.pass_version == magic.SINGLEPULSE_EXTRACTOR_PASS
        )


def append_Descriptor_to_file(descriptor, fout):
    d = descriptor
    fout.write(np.uint8(d.magic_1).tobytes())
    fout.write(np.uint8(d.magic_2).tobytes())
    fout.write(np.uint8(d.magic_3).tobytes())
    fout.write(np.uint8(d.pass_version).tobytes())
    fout.write(np.uint8(d.event_type).tobytes())


def read_Descriptor_from_file(fin):
    raw_header = np.fromstring(fin.read(5), dtype=np.uint8, count=5)
    d = Descriptor()
    d.magic_1 = raw_header[0]
    d.magic_2 = raw_header[1]
    d.magic_3 = raw_header[2]
    d.pass_version = raw_header[3]
    d.event_type = raw_header[4]
    return d


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
    number_of_pixels_and_photons = len(phs.raw)
    fout.write(np.uint32(number_of_pixels_and_photons).tobytes())
    fout.write(phs.raw.tobytes())


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
    phs.raw = np.fromstring(
        fin.read(number_of_pixels_and_photons),
        dtype=np.uint8
    )
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
        descriptor = Descriptor()
        descriptor.event_type = OBSERVATION_EVENT_TYPE_KEY
        append_Descriptor_to_file(descriptor, fout)
        append_observation_id_to_file(event.observation_info, fout)
        append_observation_info_to_file(event.observation_info, fout)
    elif hasattr(event, 'simulation_truth'):
        descriptor = Descriptor()
        descriptor.event_type = SIMULATION_EVENT_TYPE_KEY
        append_Descriptor_to_file(descriptor, fout)
        append_simulation_id_to_file(event.simulation_truth, fout)
    else:
        raise
    append_pointing_to_file(event, fout)
    append_photonstream_to_file(event.photon_stream, fout)
    append_saturated_pixels_to_file(event.photon_stream.saturated_pixels, fout)


def read_event_from_file(fin):
    try:
        descriptor = read_Descriptor_from_file(fin)
        event = Event()
        if descriptor.event_type == OBSERVATION_EVENT_TYPE_KEY:
            obs = ObservationInformation()
            read_observation_id_from_file(obs, fin)
            read_observation_info_from_file(obs, fin)
            event.observation_info = obs
        elif descriptor.event_type == SIMULATION_EVENT_TYPE_KEY:
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
    d = read_Descriptor_from_file(fin)
    return d.is_valid()


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
