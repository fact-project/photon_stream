import numpy as np
import struct


def fourChars2float32(four_byte_string):
    '''
    Interpret a string of 4 chars like 'EVTH' as a 4 byte float.
    CORSIKA uses such binary mappings to encode its header markers.
    '''
    return struct.unpack('f', four_byte_string.encode())[0]

CORSIKA_RUN_MARKER = np.float32(fourChars2float32('RUNH'))
CORSIKA_RUN_END_MARKER = np.float32(fourChars2float32('RUNE'))
CORSIKA_EVENT_MARKER = np.float32(fourChars2float32('EVTH'))

IDX_RUNH_RUN_NUMBER = 2-1

IDX_EVTH_EVENT_NUMBER = 2-1
IDX_EVTH_RUN_NUMBER = 44-1
IDX_EVTH_REUSE_NUMBER = 98-1


def read_corsika_headers_from_file(fin):
    '''
    Read in a MMCS CORSIKA run and return the raw run header and the
    raw event headers.
    '''
    c = np.frombuffer(fin.read(), dtype=np.float32)

    # RUN HEADER
    run_header = c[0:273]
    assert run_header[0] == CORSIKA_RUN_MARKER

    # EVENTS
    number_of_blocks = c.shape[0]/273
    assert number_of_blocks%1 == 0.
    number_of_blocks = int(number_of_blocks)

    event_headers = []
    for block_index in range(number_of_blocks-2):
        start = (block_index+1)*273
        end = start + 273
        event_header = c[start:end].copy()
        if (
            event_header[0] ==
            CORSIKA_EVENT_MARKER and
            event_header[IDX_EVTH_RUN_NUMBER] ==
            run_header[IDX_RUNH_RUN_NUMBER]
        ):
            event_headers.append(event_header)
    event_headers = np.array(event_headers)

    # RUN END
    start = (block_index+2)*273
    end = start + 273
    run_end = c[start:end]

    return {
        'run_header': run_header,
        'event_headers': event_headers,
        'run_end': run_end
    }


def append_corsika_headers_to_file(headers, fout):
    '''
    Write the headers read in by 'read_corsika_headers' to a file.
    '''
    fout.write(headers['run_header'])
    for event_header in headers['event_headers']:
        fout.write(event_header)
    fout.write(headers['run_end'])
