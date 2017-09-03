import os


def touch(path):
    with open(path, 'a') as out:
        os.utime(path)