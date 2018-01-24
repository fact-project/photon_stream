#! /usr/bin/env python
"""
Backup the photon-stream output to ETH Zurich.
Asserts, that only one instance is running.

Usage: phs.isdc.backup.to.ethz [options]

Options:
    -h | --help
"""
import docopt
from os.path import join
import os
from filelock import FileLock
from filelock import Timeout
import subprocess as sp


def folder_wise_rsync_a(
    destination_path,
    source_path,
    source_host='',
    destination_host='',
):
    if destination_host:
        destination_host+=':'
    if source_host:
        source_host+=':'

    for dirname, subdirs, files in os.walk(source_path):
        rel_path = os.path.relpath(dirname, source_path)
        fr = rel_path+'/'
        to = destination_host + destination_path
        cmd = "rsync -lptgodD -v --relative " + fr + " " + to
        print('\n', cmd, '\n')
        sp.call(cmd, shell=True, cwd=source_path)


def backup():
    print('Start backup to ETH Zurich')
    rsync_lock_path = join(
        '/',
        'home',
        'guest',
        'relleums',
        '.phs.isdc.backup.to.ethz.lock'
    )
    try:
        rsync_lock = FileLock(rsync_lock_path)
        with rsync_lock.acquire(timeout=3600):
            folder_wise_rsync_a(
                source_host='',
                source_path=join(
                    '/',
                    'gpfs0',
                    'fact',
                    'processing',
                    'public',
                    'phs/'
                ),
                destination_host='relleums@ihp-pc41.ethz.ch',
                destination_path=join('/', 'data', 'fact_public', 'phs/'),
            )
    except Timeout:
        print('Could not lock '+rsync_lock_path)
    print('End backup')


def main():
    try:
        docopt.docopt(__doc__)
        backup()
    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()
