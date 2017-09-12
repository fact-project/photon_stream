"""
Checks the production status of another 128 fact/raw to phs/obs conversions
and updates phs/obs/runstatus.csv with the results.

Export the FACT password: export FACT_PASSWORD=*********

Usage: phs.isdc.obs.status [options]

Options:
    -h | --help
"""
import docopt
import photon_stream as ps

def main():
    try:
        docopt.docopt(__doc__)
        ps.production.isdc.status()
    except docopt.DocoptExit as e:
        print(e)
if __name__ == '__main__':
    main()
