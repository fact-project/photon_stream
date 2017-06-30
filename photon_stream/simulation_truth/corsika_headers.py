import numpy as np
import struct

def fourChars2float32(four_byte_string):
    '''
    Interpret a string of 4 chars like 'EVTH' as a 4 byte float.
    CORSIKA uses such binary mappings to encode its header markers.
    '''
    return struct.unpack('f', four_byte_string.encode())[0]

CORSIKA_RUN_MARKER = np.float32(fourChars2float32('RUNH'))
CORSIKA_EVENT_MARKER = np.float32(fourChars2float32('EVTH'))

def read_corsika_headers(path):
    '''
    Read in a MMCS CORSIKA run and return the raw run header and the 
    raw event headers.
    '''
    c = np.fromfile(path, dtype=np.float32)
    run_header = c[0:273]
    assert run_header[0] == CORSIKA_RUN_MARKER

    number_of_blocks = c.shape[0]/273
    assert number_of_blocks%1 == 0.
    number_of_blocks = int(number_of_blocks)

    event_headers = []
    for block_index in range(number_of_blocks-1):
        start = (block_index+1)*273
        end = start + 273
        block = c[start:end]

        if block[0] == CORSIKA_EVENT_MARKER:
            event_headers.append(block)

    event_headers = np.array(event_headers)
    return {'run_header': run_header, 'event_headers': event_headers}


def write_corsika_headers(headers, path):
    '''
    Write the headers read in by 'read_corsika_headers' to a file at path.
    '''
    with open(path, 'wb') as fout:
        fout.write(headers['run_header'])
        for event_header in headers['event_headers']:
            fout.write(event_header)