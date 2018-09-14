

def is_gzipped_file(path):
    """
    Check for gzip file, see https://tools.ietf.org/html/rfc1952#page-5

    Reads in the first two bytes of a file and compares with the gzip magic
    numbers.
    """
    with open(path, 'rb') as fin:
        marker = fin.read(2)
        if len(marker) < 2:
            return False
        return marker[0] == 31 and marker[1] == 139
