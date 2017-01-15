import numpy as np
from ._input_output import append_photonstream_to_binary_file
from ._input_output import read_photonstream_from_binary_file


class PhotonStreamReader(object):
    def __init__(self, path, baselines=True):
        self.path = path
        self.file = open(path, "rb")
        self._baselines = baselines

        self.run_night = read_uint64(self.file)
        self.run_id = read_uint64(self.file)

    def __exit__(self):
        self.file.close()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            event_dict = {}
            event_dict['RunId'] = self.run_id
            event_dict['NightId'] = self.run_night
            event_dict['EventId'] = read_uint32(self.file)
            event_dict['TriggerType'] = read_uint32(self.file)
            event_dict['UnixTimeUTC'] = [read_uint32(self.file), read_uint32(self.file)]
            event_dict['AzPointing'] =  read_float32(self.file)
            event_dict['ZdPointing'] = read_float32(self.file)
            event_dict['PhotonStream'] = read_photonstream_from_binary_file(self.file)
            if self._baselines:
                event_dict['BaseLines'] = np.fromfile(
                    self.file, 
                    dtype=np.int16, 
                    count=1440)

            return event_dict
        except:
            raise StopIteration

    def __repr__(self):
        out = 'SpeGzipReader('
        out += self.path+')\n'
        return out


def read_uint64(f):
    return np.fromfile(f, dtype=np.uint64, count=1)[0]


def read_uint32(f):
    return np.fromfile(f, dtype=np.uint32, count=1)[0]


def read_float32(f):
    return np.fromfile(f, dtype=np.float32, count=1)[0]