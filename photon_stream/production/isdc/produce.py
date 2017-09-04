#! /usr/bin/env python
"""
Converting FACT raw observation runs into photon-stream runs. You need to export
the universal FACT password: export FACT_PASSWORD=*********

Usage: phs.isdc.obs.produce [options]

Options:
    -h | --help
"""
import docopt
import photon_stream as ps

def main():
    try:
        docopt.docopt(__doc__)
        ps.production.isdc.produce()
    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()