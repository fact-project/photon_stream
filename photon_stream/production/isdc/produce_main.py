#! /usr/bin/env python
"""
Convert another chunk of fact/raw/ observation runs into phs/obs/ runs. The
chunk size depends on the demand (output already exists) and wheter qstat is
busy. The maximum chunk size is 128 runs.

Export the FACT password: export FACT_PASSWORD=*********

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
