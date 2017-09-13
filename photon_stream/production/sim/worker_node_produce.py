"""
Usage: phs.sim.produce.worker [options]

Options:
    --ceres_events_path=PATH
    --corsika_path=PATH
    --out_dir=PATH
"""
import docopt
import photon_stream as ps


def main():
    try:
        arguments = docopt.docopt(__doc__)
        ps.production.sim.(
            ceres_events_path=arguments['--ceres_events_path'], 
            corsika_path=arguments['--corsika_path'], 
            out_dir=arguments['--out_dir'],
        )
    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()
