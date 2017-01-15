import numpy as np
from .PhotonStream import PhotonStream

def read_photonstream_from_raw_photonstream(
    raw_photon_stream, 
    slice_duration):

    rps = PhotonStream()
    rps.slice_duration = np.float64(slice_duration)
    rps.time_lines = raw_photon_stream
    return rps

def append_photonstream_to_binary_file(photonstream, file_handle):
    
    # WRITE NUMBER OF TIMELINES
    number_of_time_lines = np.uint64(len(photonstream.time_lines))
    file_handle.write(number_of_time_lines.tobytes())

    # WRITE NUMBER OF PHOTONS
    number_of_photons = np.uint64(photonstream._number_photons())
    file_handle.write(number_of_photons.tobytes())

    # WRITE SLICE DURATION
    slice_duration = np.float64(photonstream.slice_duration)
    file_handle.write(slice_duration.tobytes())

    # DETERMINE SLICE WIDTH IN BYTE
    min_slice, max_slice = photonstream._min_max_arrival_slice()
    if max_slice < np.iinfo(np.uint8).max:
        dtype = np.uint8
    elif max_slice < np.iinfo(np.uint16).max:
        dtype = np.uint16      
    elif max_slice < np.iinfo(np.uint32).max:
        dtype = np.uint32
    elif max_slice < np.iinfo(np.uint64).max:
        dtype = np.uint64
    else:
        raise

    # WRITE SLICE WIDTH IN BYTE
    slice_width = np.uint8(dtype().itemsize)
    file_handle.write(slice_width.tobytes())

    # WRITE PHOTON ARRIVAL SLICES 
    linebreak = np.array([np.iinfo(dtype).max], dtype=dtype)
    for pixel_arrivals in photonstream.time_lines:
        arrivals = np.array(pixel_arrivals, dtype=dtype)
        if arrivals.shape[0] > 0:
            file_handle.write(arrivals.tobytes())
        file_handle.write(linebreak.tobytes())

def read_photonstream_from_binary_file(file_handle):
    ps = PhotonStream()

    # READ NUMBER OF TIMELINES
    number_of_time_lines = np.fromfile(file_handle, dtype=np.uint64, count=1)[0]

    # READ NUMBER OF PHOTONS
    number_of_photons = np.fromfile(file_handle, dtype=np.uint64, count=1)[0]

    # READ SLICE DURATION
    slice_duration = np.fromfile(file_handle, dtype=np.float64, count=1)[0]
    ps.slice_duration = slice_duration

    # READ SLICE WIDTH IN BYTE
    slice_width = np.fromfile(file_handle, dtype=np.uint8, count=1)[0]

    if slice_width == np.uint8().itemsize:
        dtype = np.uint8()
    elif slice_width == np.uint16().itemsize:
        dtype = np.uint16()
    elif slice_width == np.uint32().itemsize:
        dtype = np.uint32()        
    elif slice_width == np.uint64().itemsize:
        dtype = np.uint64()
    else:
        raise

    # READ PHOTONSTREAM
    photn_stream = np.fromfile(
        file_handle, 
        dtype=dtype, 
        count=number_of_photons+number_of_time_lines)

    linebreak = np.array([np.iinfo(dtype).max], dtype=dtype)

    ps.time_lines = []
    time_line = []
    for arrival_slice in photn_stream:
        if arrival_slice == linebreak:
            ps.time_lines.append(time_line.copy())
            time_line.clear()
        else:
            time_line.append(arrival_slice)
    return ps