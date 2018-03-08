import os
from os.path import join
from .extract_single_photons import extract_single_photons
from .extract_corsika_headers import extract_corsika_headers

RUN_NUMBER_DIGITS = 5

_fact_tools_jar_path = join(
    '/', 'net', 'big-tank', 'POOL', 'projects', 'fact', 'smueller',
    'fact-tools', 'target', 'fact-tools-0.18.1.jar'
)


def produce_single_simulation_run(
    ceres_events_path,
    corsika_path,
    out_dir,
    fact_tools_jar_path=_fact_tools_jar_path
):
    ceres_basename = os.path.basename(ceres_events_path)
    corsika_basename = os.path.basename(corsika_path)

    ceres_run = int(ceres_basename.split('.')[0])
    corsika_run = int(corsika_basename[3:3+RUN_NUMBER_DIGITS+1])

    assert ceres_run == corsika_run

    os.makedirs(out_dir, exist_ok=True, mode=0o755)

    corsika_header_path = '{run:06d}.ch.gz'.format(run=ceres_run)
    phs_basename = '{run:06d}'.format(run=ceres_run)

    corsika_header_path = join(out_dir, corsika_header_path)

    extract_corsika_headers(
        in_path=corsika_path,
        out_path=corsika_header_path
    )

    extract_single_photons(
        ceres_path=ceres_events_path,
        out_dir=out_dir,
        out_basename=phs_basename,
        fact_tools_jar_path=fact_tools_jar_path,
        o_path=join(out_dir, '{run:06d}.o'.format(run=ceres_run)),
    e_path=join(out_dir, '{run:06d}.e'.format(run=ceres_run)),
    )
