#! /usr/bin/env python
"""
Usage: worker_node_status.py --phs_path=PATH --status_path=PATH --o_path=PATH --e_path=PATH

Options:
    --phs_path=PATH
    --status_path=PATH
    --o_path=PATH
    --e_path=PATH
"""
import docopt
import os
import shutil
import numpy as np
import json
import fact
from photon_stream.production.tools import number_of_events_in_file


def status(phs_path, status_path, o_path, e_path):
    stat = {}
    r = fact.path.parse(phs_path)
    stat['fNight'] = r['night']
    stat['fRunID'] = r['run']


    # PhsSize
    #--------
    stat['PhsSize'] = np.nan
    try:
        stat['PhsSize'] = os.stat(phs_path).st_size
    except:
        pass


    # NumActualPhsEvents
    #-------------------
    stat['NumActualPhsEvents'] = np.nan
    try:
        stat['NumActualPhsEvents'] = number_of_events_in_file(phs_path)
    except:
        pass


    # StdOutSize
    #-----------
    stat['StdOutSize'] = np.nan
    try:
        stat['StdOutSize'] = os.stat(o_path).st_size
    except:
        pass


    # StdErrorSize
    #-------------
    stat['StdErrorSize'] = np.nan
    try:
        stat['StdErrorSize'] = os.stat(e_path).st_size
    except:
        pass

    with open(status_path+'.part', 'wt') as fout:
        json.dump(stat, fout)
    shutil.move(status_path+'.part', status_path)


def main():
    try:
        args = docopt.docopt(__doc__)
        status(
            phs_path=args['--phs_path'], 
            status_path=args['--status_path'],
            o_path=args['--o_path'], 
            e_path=args['--e_path']
        )
    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()
