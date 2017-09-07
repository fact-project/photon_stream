#! /usr/bin/env python
"""
Syncronize the local phs/obs/runstatus.csv with the latest runinfo database from
La Palma.
Export the FACT password: export FACT_PASSWORD=*********

Usage: phs.isdc.obs.synclapalma [options]

Options:
    -h | --help
"""
import docopt
import photon_stream as ps

def main():
    try:
        docopt.docopt(__doc__)
        ps.production.runstatus.update_to_latest(
        	obs_dir=join('/gpfs0','fact','processing','public','phs','obs')
        )
    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()