"""
Usage: worker_node_status.py --phs_path=PATH --status_path=PATH

Options:
    --phs_path=PATH
    --status_path=PATH
"""
import docopt
import os
from os.path import exists
from os.path import dirname
from os import makedirs
import shutil
import numpy as np
import json
import fact
from photon_stream.EventListReader import EventListReader


def status(phs_path, status_path):
    stat = {}
    r = fact.path.parse(phs_path)
    stat['fNight'] = r['night']
    stat['fRunID'] = r['run']

    # NumActualPhsEvents
    #-------------------
    stat['NumActualPhsEvents'] = np.nan
    if exists(phs_path):
        i = 0
        try:
            for evt in EventListReader(phs_path):
                i += 1
        except:
            pass
        stat['NumActualPhsEvents'] = i

    makedirs(dirname(status_path), exist_ok=True, mode=0o755)
    with open(status_path+'.part', 'wt') as fout:
        json.dump(stat, fout)
    shutil.move(status_path+'.part', status_path)


def main():
    try:
        args = docopt.docopt(__doc__)
        status(
            phs_path=args['--phs_path'], 
            status_path=args['--status_path'],
        )
    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()
