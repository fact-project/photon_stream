from distutils.core import setup

setup(
    name='photon_stream',
    version='0.0.1',
    description='Read, write, manipulate and plot a Photon Stream',
    url='https://github.com/fact-project/',
    author='Sebastian Achim Mueller',
    author_email='sebmuell@phys.ethz.ch',
    license='MIT',
    packages=[
        'photon_stream',
        'photon_stream.production',
        'photon_stream.production.ethz',
        'photon_stream.experimental',
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
        'sklearn',
        'scikit-image',
        'matplotlib',
        'pyfact',
        'pandas',
        'tqdm'
    ],
    entry_points={'console_scripts': [
        'phs_extract_muons = photon_stream.muons.isdc_production.worker_node_main:main',
    ]},
    zip_safe=False,
)
