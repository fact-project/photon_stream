import numpy as np
from . import io 


def list_of_lists_to_raw_phs(lol):
    number_photons = number_photons_in_list_of_list(lol)
    number_symbols = number_photons + io.magic_constants.NUMBER_OF_PIXELS 
    raw = np.zeros(number_symbols, dtype=np.uint8)
    i = 0
    for time_series in lol:
        raw_time_series = np.array(time_series, dtype=np.uint8)
        j = raw_time_series.shape[0]
        raw[i:i+j] = raw_time_series
        i += j
        raw[i] = io.binary.LINEBREAK
        i += 1
    return raw


def raw_phs_to_list_of_lists(raw_phs):
    time_lines = []
    if len(raw_phs) > 0:
        time_lines.append([])

    pixel = 0
    for i, symbol in enumerate(raw_phs):
        if symbol ==  io.binary.LINEBREAK:
            pixel += 1
            if i+1 < len(raw_phs):
                time_lines.append([])
        else:
            time_lines[pixel].append(int(symbol))
    return time_lines


def number_photons_in_list_of_list(lol):
    number_photons = 0
    for pixel_time_series in lol:
        number_photons += len(pixel_time_series)
    return number_photons


def raw_phs_to_point_cloud(raw_phs, cx, cy):
    number_photons = len(raw_phs) - io.magic_constants.NUMBER_OF_PIXELS
    cloud = np.zeros(shape=(number_photons,3))
    pixel_chid = 0
    p = 0
    for s in raw_phs:
        if s == io.binary.LINEBREAK:
            pixel_chid += 1
        else:
            cloud[p,0] = cx[pixel_chid]
            cloud[p,1] = cy[pixel_chid]
            cloud[p,2] = s*io.magic_constants.TIME_SLICE_DURATION_S
            p += 1
    return cloud


def raw_phs_to_image_sequence(raw_phs):
    image_sequence = np.zeros(
        shape=(
            io.magic_constants.NUMBER_OF_TIME_SLICES,
            io.magic_constants.NUMBER_OF_PIXELS
        ),
        dtype=np.int16,
    )
    pixel_chid = 0
    for s in raw_phs:
        if s == io.binary.LINEBREAK:
            pixel_chid += 1
        else:
            image_sequence[
                s - io.magic_constants.NUMBER_OF_TIME_SLICES_OFFSET_AFTER_BEGIN_OF_ROI, 
                pixel_chid
            ] += 1 

    return image_sequence