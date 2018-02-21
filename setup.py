from distutils.core import setup

setup(
    name='photon_stream',
    version='0.0.6',
    description='Read, write, manipulate and plot a Photon Stream',
    url='https://github.com/fact-project/',
    author='Sebastian Achim Mueller',
    author_email='sebmuell@phys.ethz.ch',
    license='MIT',
    packages=[
        'photon_stream',
        'photon_stream.io',
        'photon_stream.production',
        'photon_stream.production.ethz',
        'photon_stream.production.isdc',
        'photon_stream.production.sim',
        'photon_stream.muons',
        'photon_stream.simulation_truth',
        'photon_stream.muons.isdc_production',
    ],
    package_data={
        'photon_stream': [
            'tests/resources/*',
            'production/resources/*',
        ]
    },
    install_requires=[
        'docopt',
        'scipy',
        'scikit-learn',
        'scikit-image',
        'matplotlib',
        'pyfact',
        'pandas',
        'tqdm',
        'ujson',
        'qstat',
        'filelock'
    ],
    entry_points={'console_scripts': [
        'phs_extract_muons = ' +
        'photon_stream.muons.isdc_production.worker_node_main:main',
        'phs.isdc.obs.synclapalma = ' +
        'photon_stream.production.isdc.synclapalma_main:main',
        'phs.isdc.obs.produce = ' +
        'photon_stream.production.isdc.produce_main:main',
        'phs.isdc.obs.produce.worker = ' +
        'photon_stream.production.isdc.worker_node_produce:main',
        'phs.isdc.obs.status = ' +
        'photon_stream.production.isdc.status_main:main',
        'phs.isdc.obs.status.worker = ' +
        'photon_stream.production.isdc.worker_node_status:main',
        'phs.sim.produce.worker = ' +
        'photon_stream.production.sim.worker_node_produce:main',
        'phs.isdc.backup.to.ethz = ' +
        'photon_stream.production.backup_main:main',
    ]},
    zip_safe=False,
)
