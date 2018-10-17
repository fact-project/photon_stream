from distutils.core import setup

setup(
    name='photon_stream',
    version='0.0.7',
    description='Read, write, manipulate and plot a Photon Stream',
    url='https://github.com/fact-project/',
    author='Sebastian Achim Mueller',
    author_email='sebmuell@phys.ethz.ch',
    license='MIT',
    packages=[
        'photon_stream',
        'photon_stream.io',
        'photon_stream.simulation_truth',
    ],
    package_data={
        'photon_stream': [
            'tests/resources/*',
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
    zip_safe=False,
)
