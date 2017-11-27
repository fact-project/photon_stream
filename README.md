# The FACT Photon-Stream [![Build Status](https://travis-ci.org/fact-project/photon_stream.svg?branch=master)](https://travis-ci.org/fact-project/photon_stream)

 - [All FACT events (observations and simulations)](https://ihp-pc41.ethz.ch/public/phs/)
 - [White Paper ICRC2017](https://pos.sissa.it/301/801/pdf)
 - [Video presentation](https://www.youtube.com/watch?v=F0C2tcj1rb8)
 - [C++ reader and writer](https://github.com/fact-project/photon_stream_cpp)

The photon-stream is based on the [single photon extractor](https://github.com/fact-project/single_photon_extractor). The events of the FACT Imaging Atmospheric Cherenkov Telecope (IACT) can be represented as a list of lists of arrival times of individual night-sky-background and air-shower photons. We call this list of lists the photon-stream.
This python package collects tools to produce, visualize and analyse photon-stream (phs) events.

## Install
```bash
pip install git+https://github.com/fact-project/photon_stream
```

## Python API
```python
import photon_stream as ps
import matplotlib.pyplot as plt

reader = ps.EventListReader('20151001_011.phs.jsonl.gz')
event = next(reader)

ps.plot.event(event)
plt.show()
```
Read in the full CORSIKA simulation truth and estimate instrument response functions:
```python
import photon_stream as ps
import pandas as pd

sim_reader = ps.SimulationReader(
    photon_stream_path='tests/resources/011014.phs.jsonl.gz',
    mmcs_corsika_path='tests/resources/011014.ch'
)

for event in sim_reader:
    # process event ...
    # extract Hillas and other features ....
    # do deep learning ...
    pass

thrown_events = pd.DataFrame(sim_reader.thrown_events())
```


![img](example/example_event_small.gif)

# The Photon-Stream Rationale
As a technology demonstrater, the FACT telescope records its observations in a format which is as close to the read out hardware as possible. This was a great choice to explore the novel SIPM and DRS4 readout chain, but turns out to be tedious to do high level physics analysis as flux, spectra and light-curve investigations on astronomical sources as the raw events are rather bulky, full of artifacts and not calibrated at all. The raw events are ```1440``` pixels X  ```300``` time slices X ```16```bit dynamic range = 864kB in size. The raw events can not be analyzed independent of each other (readout artifacts) and furhter need additional calibration files, which are not straight forward to identify. Although effort was spent to compress the raw events with a dedicated format called [zfits](https://arxiv.org/pdf/1506.06045.pdf), the events from 2011 to 2017 still need 450TB of disk storage. The years passed by and FACT is not longer a demonstrater, but a part of the high energy gamma-ray astronomy community. It is time to analyse our observations in an easier way. It is time for a physics format.

The photon-stream can compress events down to a size of 3.7kB for dark nights. Based on this, the idea was born to create a no compromise, physics only file format for the FACT telescope with the potential to fit all events from 2011 to 2017 on a single hard disk drive of 10TB.
The photon-stream format is already fully calibrated and does not need additional files to be interpreted. Further all instrument artifacts have been removed and the events are now independent of each other.

The photon-stream format is intended and optimized to do __astronomy__. We belive, that for effective physics analysis it is crucial to have the observed events as small in storage space as any possible. We want to enable a Bachelor student to analyse years of FACT observations on her notebook! We want to enable our students to transfer a full 5min FACT observation run via email. We want to give our students something that they are familiar with, i.e. the concept of single photons instead of readout calibration and artifact foo. We want to keep as much of the air shower physics as possible and even gain additional knowledge which was not accessible with our current 'one arrival time only' policy which is still a heritage of our PMT based ancestors. Finally, we want to reveal, for the first time ever, the true potential of an SIPM based IACT. This is the FACT photon-stream.

# Memory representations
Depending on the computaional task, the information in the photon-stream can be represented in different ways in memory which can ease the processing. These different representations can be converted into each other without information losses.

## List-of-lists
The list-of-lists in-memory representation is an outer list of all pixels (CHID ordering) that loops over the extracted arrival time lists for each pixel. The list-of-lists in-memory representation is the most compact one. We use the list-of-lists in-memory representation for permanent storage.

## Image-sequence
A two dimensional histogram along the the arrival time slices and the pixel directions. Each bin counts the number of single photons arriving at its corresponding pixel and corresponding arrival time slice. The image-sequence in-memory representation is suitable when a fixed event size is preferred. The histogram is always the same size in memory regardless of the number or structure of the photons. Slicing and integrating along the time axis can produce classic images with one intensity for each pixel.

## Point-cloud
A list of three dimensional direction and time coordinates of all photons in the stream of an event. Two of the three dimensions describe the angular incoming direction of a photon, which correspond to a specific pixel. The third dimension is the arrival time of the photon. This point-cloud in-memory representation is ideal for plotting the 3D point cloud, or to perform the density based clustering to tell apart air-shower photons from night-sky-background photons.


# Storage: Json-Lines format
This human readable format is easy to understand and used as widely as the internet is wide. Fortunately gzipped Json-Lines is only ```15%``` to ```35%``` larger than the smallest custom binary format we could come up with. The read and right speed is sufficient for physics analysis (DBSCAN clustering).
```json
{"Night":20170119,"Run":229,"Event":1,"UnixTime_s_us":[1484895178,532244],"Trigger":4,"Az_deg":-63.253664797474336,"Zd_deg":33.06900475126648,"PhotonArrivals_500ps":[[59,84],[102,93,103],[58],[65,79,97],[],[125,43,68],[102],[68,100,123],[52,52,79,113,61,78,112,87]],"SaturatedPixels":[]}
```
Json-Lines run files are named ```YYYYmmnn_RRR.phs.jsonl.gz```. There is no run header. Each line in a ```phs.jsonl.gz``` file corresponds to one event. This way events can be concatenated and counted very easily.

### Keys

```json
"Night":YYYYmmnn
```
The FACT night integer. Here ```YYYY``` is the year A.D., ```mm``` is the month, and ```nn``` is the night of the observation. A night is different from a day. The night integer increases to the next night during ```12:00 UTC``` o'clock rather than ```00:00 UTC```. The night integer is always 8 digits, e.g. ```20170201``` which is first of February 2017.

```json
"Run":RRR
```
The unique run identifier of a night. The observations of a night are split into runs of usually ```5 minutes```. Since not all runs are observation runs, but e.g. calibration runs, the run identifiers in the high level photon-stream format are not neccessary continous, since calibration runs are missing. The run integer in the file name is always 3 digits, e.g. ```20170201_021.phs.jsonl.gz``` is the twentyfirst run of the first night in February 2017.

```json
"Event":eee
```
The event identifier of a run. In a run, the individual events have unique identifiers. The event integer is not fixed in its length e.g. ```"Event":4``` is the fourth event in a run, and ```"Event":34845``` is the thirty-four-thousands-and-eight-hundreds-fourty-fifth event in a run.

```json
"UnixTime_s_us":[1484895178,532244]
```
The moment when the event was recorded in unix time (keep in mind that unix time has leap seconds!). The first entry in the the array are the unix time seconds ```s```, and the second entry are the additional micro seconds ```us```.
```c++
double event_time = 1484895178.0 + 1e-6 * 532244.0
```
The time stamp is out of the FACT event builder program and can be off the actual trigger time by about ```30ms```. For high precision timing in the ```5us``` range, the GPS time is needed, which unfortunally is not yet available.

```json
"Trigger":xxxx
```
The trigger type of the FACT telescope. There are differnt trigger types for FACT, here in the high level format we only have left:

- 4: The self triggered mode, also called "physics trigger". These events are expected to contain light flashes and air showers.
- 1: External trigger input 1. Here the GPS module triggers the read out ```59``` times a minute. These events are expected to contain only night-sky-background.
- 2: External trigger input 2. The same as external trigger input 1, since the GPS modul was switched from 1 to 2 once.
- 1024: A random trigger also called "pedestal trigger". These events are also expected to only contain night-sky-background.

For a full overview of the FACT trigger types, see the [Phd of Patrick Vogler, table 4.3.b](http://e-collection.library.ethz.ch/eserv/eth:48381/eth-48381-02.pdf)

```json
"Az_deg":-63.253664797474336,"Zd_deg":33.06900475126648
```
The pointing direction of the FACT telescope in the moment the event was recorded. This is reconstructed from the ```aux``` (auxilluarry) drive files based on the event time.  ```"Az_deg"``` is the azimuth pointing in degrees, and ```"Zd_deg"``` is the zenith distance pointing in degrees.

```json
"PhotonArrivals_500ps":[[],[],[]]
```
The actual photon-stream. A list of lists of arrival times of photons in units of ```500ps```.
The outer list loops over all ```1440``` pixels of FACT and is ordered in ```Continuous  Hardware ID (CHID)```. The inner lists loop over the arrival times of the individual photons for the corresponding pixel. The maximum number of photons in a pixel before the extraction of photons is aborted is ```500```. If there are ```500``` photons in a pixel, this pixel is saturated and meaningless.
Since a single photon is now defined by only one sharp arrival time in contrast to a very long pulse, there is no need anymore to stick to a long region of interest in time and therefore the output of the photon-stream is truncated only to the region where the air-shower physics takes place, which is from ```15ns``` to ```65ns``` (I hardly ever saw air shower events beyond ```45ns```) on FACT's raw ROI of ```150ns```. So each event has an exposure time of ```50ns```. If you have any uncomfortable feelings about this truncation then let me remind you of the physics results which come out of the MAGIC telescope with its ROI of ```30ns``` and only ```625ps``` sampling.

```json
"SaturatedPixels":[123,456]
```
A list of pixels in ```CHID``` to indicate that the corresponding pixel had an saturated analog time line out of the raw DRS4 chip. The maximim number of saturated pixels is ```100```, as the event is skipped then anyhow. Usually this list is empty. Such saturations happen not only for ultra high energy air showers, but also when the DRS4 calibration was not possible or is broken elseway.

# Storage: phs binary format
The ```phs``` format is a binary format with exactly the same content as the Json-Lines ```phs.jsonl``` format.
The binary format is about ```15%``` to ```35%``` smaller than the Json-Lines and allows much higher read speeds.
There is no run header of footer. This is just a list of events. Each event hat its full ID.
Binary run files are named ```YYYYmmnn_RRR.phs.gz```.

The content of the differnt event types is as follows:

## Observation Event
    - Descriptor
    - Observation Event Identifier
    - Observation Information
    - Pointing
    - Photon-Stream
    - Saturated Pixels


## Simulation Event
    - Descriptor
    - Simulation Event Identifier
    - Pointing
    - Photon-Stream
    - Saturated Pixels


### Descriptor (5 Byte)
    char
    +--------+--------+--------+
    |    p   |    h   |    s   |
    +--------+--------+--------+
    - A magic descriptor 'phs'

    uint8
    +--------+
    |VERSION |
    +--------+
    - VERSION == 4 is pass4

    uint8
    +--------+
    |  Type  |
    +--------+
    - Type == 0 is Observation
    - Type == 1 is Simulation


### Observation Event Identifier (12 Byte)

    uint32
    +--------+--------+--------+--------+
    |              Night Id             |
    +--------+--------+--------+--------+

    uint32
    +--------+--------+--------+--------+
    |               Run Id              |
    +--------+--------+--------+--------+

    uint32
    +--------+--------+--------+--------+
    |             Event Id              |
    +--------+--------+--------+--------+

### Simulation Event Identifier (12 Byte)

    uint32
    +--------+--------+--------+--------+
    |           CORSIKA RUN Id          |
    +--------+--------+--------+--------+

    uint32
    +--------+--------+--------+--------+
    |         CORSIKA EVENT Id          |
    +--------+--------+--------+--------+

    uint32
    +--------+--------+--------+--------+
    |      CORSIKA Event Reuse Id       |
    +--------+--------+--------+--------+

### Pointing (8 Byte)

    float32
    +--------+--------+--------+--------+
    |       Zenith Distance [Deg]       |
    +--------+--------+--------+--------+

    float32
    +--------+--------+--------+--------+
    |         Azimuth  [Deg]            |
    +--------+--------+--------+--------+


### Observation Information (12 Byte)

    uint32
    +--------+--------+--------+--------+
    |          UNIX time [s]            |
    +--------+--------+--------+--------+

    uint32
    +--------+--------+--------+--------+
    |      UNIX time [us] mod. [s]      |
    +--------+--------+--------+--------+

    uint32
    +--------+--------+--------+--------+
    |            Trigger type           |
    +--------+--------+--------+--------+


### Photon-Stream  (number photons + number pixel Byte)

    uint32
    +--------+--------+--------+--------+
    |  Number of pixels plus photons    |
    +--------+--------+--------+--------+
    The size of the photon-stream in bytes.


    Photon arrival times in slices
    EXAMPLE. The actual shape and structure depent on the specific event.

         uint8
         +--------+--------+--------+--------+
       0 |     A  |     B  |     C  |   255  | <- Pixel CHID=0, 3 photons, arrival slices A, B, and C.
         +--------+--------+--------+--------+
       1 |   XXX  |   XXX  |   255  |
         +--------+--------+--------+
       2 |     C  |   255  | <- Pixel CHID=2, 1 photons, arriving in slice C.
         +--------+--------+--------+--------+--------+
       3 |   XXX  |   XXX  |   XXX  |   XXX  |   255  |
         +--------+--------+--------+--------+--------+--------+--------+
       4 |   XXX  |   XXX  |   XXX  |   XXX  |   XXX  |   XXX  |   255  |
         +--------+--------+--------+--------+--------+--------+--------+
       5 |   XXX  |   255  |
         +--------+--------+
       6 |   255  | <- Pixel CHID=6, 0 photons, empty.
         +--------+--------+--------+
       7 |   XXX  |   XXX  |   255  |
         +--------+--------+--------+
       .
       .
       .
         +--------+--------+
    1437 |   XXX  |   255  |
         +--------+--------+--------+--------+--------+
    1438 |   XXX  |   XXX  |   XXX  |   XXX  |   255  |
         +--------+--------+--------+--------+--------+
    1439 |     D  |     E  |   255  | <- last pixel CHID=1439, 2 photons at slices D and E.
         +--------+--------+--------+
    Pixel
    CHID

A list of lists of photon arrival time slices in CHID pixel order.
The line break from one pixel to the next pixel is marked by the linebreak
symbol 2^8-1 = ```255```. This leaves 255 (0-254) slices to encode photon arrival times.

### Saturated Pixels (2 + 2*number saturated pixel Byte)

    uint16
    +--------+--------+
    |        N        |
    +--------+--------+
    Number of saturated pixels

    uint16
    +--------+--------+--------+--------+     +--------+--------+
    |      CHID 0     |      CHID 1     | ... |      CHID N-1   |
    +--------+--------+--------+--------+     +--------+--------+
    A list of CHIDs of saturated pixels


## Integration into existing air shower reconstruction software
When the idea of the photon-stream is inverted, the amplitude time lines of an individual pixel can be reconstructed from the photon-stream events which enables FACT to use ist usual air shower reconstruction programs right ahead without modifications.


## Where to go from here
- explore an intermediate file format based on the photon stream, only photons no noise
- explore novel image cleaning by combining the temporal and directional information of all pixels before cutting (DBSCAN clustering)
- ...
