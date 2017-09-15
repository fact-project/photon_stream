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
from filelock import FileLock
from filelock import Timeout
import subprocess as sp


def backup(
    from_here=join('/','gpfs0','fact','processing','public','phs/'),
    to_there='relleums@ethz:'+join('/','data','fact_public','phs/')
):
"""
rsync -av /gpfs0/fact/processing/public/phs/ relleums@ethz:/data/fact_public/phs/
"""
    print('Start backup to ETH Zurich')
    rsync_lock_path = join(from_here, '.rsync.ethz.lock')
    try:
        rsync_lock = FileLock(rsync_lock_path)
        with runstatus_lock.acquire(timeout=3600):
            sp.call(['rsync', '-av', from_here, to_there,])
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