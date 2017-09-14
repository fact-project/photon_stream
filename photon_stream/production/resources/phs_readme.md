# Photon-Stream

All events of the First Geiger mode Avalanche Cherenkov Telescope [FACT](http://fact-project.org/) in the photon-stream representation. Every single Cherenkov and night sky background photon that was ever either recorded or simulated with FACT is stored here.

Learn how to [read and interpret the photon-stream](https://github.com/fact-project/photon_stream).

Read also our introduction article for the photon-stream ```phs_introduction.pdf```, right next to this README.

## Observations ./obs/

The processing and availability status of the observation runs can be found here:

```./obs/runstatus.csv```

The ```./obs/runstatus.csv``` is a tabular cache of the photon-stream production status. 

If ontime and accurate fluxes are important for your analysis, only use runs where ```IsOk``` is ```1```. To be sure that a photon-stream output file is valid, we compare the ```NumExpectedPhsEvents``` and the ```NumActualPhsEvents```. We know (for most runs) the ```NumExpectedPhsEvents``` from the FACT runinfo database on La Palma and can count the ```NumActualPhsEvents``` in the output files. If both numbers are equal, the run is considered to be valid and is marked with a ```1``` in the ```IsOk``` column. The ```./obs/runstatus.csv``` can be reproduced using only the photon-stream output and the runinfo database.

Observations are stored in a time structure e.g. ```./obs/2017/09/13/20170913_144.phs.jsonl.gz``` is the 144th run on 13th of September in year 2017.


## Simulations ./sim/

The Dortmund simulations of [Ceres pass 12](https://trac.fact-project.org/browser/fact/MonteCarloSettings/Ceres/standard/ceres_12.rc).

There are protons, gamma, and helium primary particles. 

- ```./sim/proton/```

- ```./sim/gamma/```

- ```./sim/helium/```

The particle types are divided into chunks with names like 'werner' or 'klaus'. The names have no meaning. For example:

- ```./sim/proton/yoda/```

In a simulation chunk there are simulation runs. Each run consists of:

- Photon-stream telescope response ```./sim/proton/yoda/XXXXXX.phs.jsonl.gz``` with all events in the run ```XXXXXX``` that lead to a read out trigger.

- Corresponding CORSIKA run and event headers ```./sim/proton/yoda/XXXXXX.ch.gz``` of all events in the run. This file is still a valid MMCS CORSIKA file, but does not contain Cherenkov photons anymore. This file is mandatory to estimate the number of thrown events to calculate the instrument response function.

- The stdout and stderror of the fact-tools single pulse extractor ```./sim/proton/yoda/XXXXXX.o``` and ```./sim/proton/yoda/XXXXXX.e```

- Baseline telescope response ```./sim/proton/yoda/XXXXXX.bsl.jsonl.gz``` which is maybe, or maybe not useful to read in the photon-stream back into an existing air-shower feature generator e.g. fact-tools.

### Author
Sebastian A. Mueller, ETH Zurich