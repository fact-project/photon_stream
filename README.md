# The FACT Photon Stream [![Build Status](https://travis-ci.org/fact-project/photon_stream.svg?branch=master)](https://travis-ci.org/fact-project/photon_stream)
The photon stream is based on the [single photon extractor](https://github.com/fact-project/single_photon_extractor). The events of the FACT Imaging Atmospheric Cherenkov Telecope (IACT) can be represented as photon stream using the single photon extractor.
In a photon stream, the single photon arrival times are stored for each read out channel (image pixel).

## Install
```bash
pip install git+https://github.com/fact-project/photon_stream
```

## Python API
```python
import photon_stream as ps
import matplotlib.pyplot as plt

run = ps.Run('20151001_011.jsonl.gz')
event = next(run)
event.plot()

plt.show()
```
![img](example/example_event_small.gif)

## Where to go from here
- explore an intermediate file format based on the photon stream, only photons no noise
- explore novel image cleaning by combining the temporal and directional information of all pixels before cutting (DBSCAN clustering)

# The Photon Stream Format Rationale
As a technology demonstrater, the FACT telescope records its observations in a data format which is as close to the read out hardware as possible. This was a great choice to explore the novel SIPM and DRS readout chain, but is rather tedious to do high level physics analysis as flux, spectra and light-curve investigations on the astronomical sources. These raw events are ```1440``` pixels x  ```300``` time slices x ```16```bit dynamic range = 864kB in size. They can not be analyzed independent of each other since readout artifacts can only be removed with knowledge on the previous event, and an additional calibration file for the DRS is needed, which is not straight forward to identify. Although effort was spent to compress the raw events with a dedicated format ```zfits```, the events shrunk only by a factor of about 3 down to about 290kB in size.

Now using the photon stream, we can compress events down to a size of 4.5kB for dark nights. Based on this, the idea was born to create a no compromise, only physics file format for the FACT telescope with the potential to fit all events from 2011 to 2017 on a single hard disk drive of 10TB.
The photon stream format is already fully calibrated and does not need additional files to be interpreted. Further all instrument artifacts have been removed and the events are now truely independent of each other.

The photon-stream format is not inteded to investigate anything of the FACT detector, but only to do astronomy!

## File Format
After evaluation of several formats (FITS, massage pack, JSON, custom binary), JSON-lines with gzip was chosen.
The following shows an example event in the final format:
```json
{"Night":20170119,"Run":229,"Event":1,"UnixTime_s_us":[1484895178,532244],"Trigger":4,"Az_deg":-63.253664797474336,"Zd_deg":33.06900475126648,"PhotonArrivals_500ps":[[59,84],[102,93,103],[58],[65,79,97],[],[125,43,68],[102],[68,100,123],[52,52,79,113,61,78,112,87], ... ],"SaturatedPixels":[]}
```
The run files will be named ```YYYYmmnn_RRR.phs.jsonl.gz```.
It turned out, that gzipped JSON-lines has only a size overhead of ```1.15``` compared to the smallest possible binary format we could come up with. Since the possibility for new students is pretty much ```0.0``` to read our custom binary, but almost ```1.0``` to read JSON-Lines, we decided to go with JSON-Lines for now.

```json
"Night":YYYYmmnn
```
The FACT night integer. Here ```YYYY``` is the year A.D., ```mm``` is the month, and ```nn``` is the night of the observation. A night is different from a day. The night integer increases to the next night during ```12:00 UTC``` o'clock rather than ```00:00 UTC```. The night integer is always 8 digits, e.g. ```20170201``` which is first of February 2017.

```json
"Run":RRR
```
The unique run identifier of a night. The observations of a night are split into runs of usually ```5 minutes```. Since not all runs are observation runs, but e.g. calibration runs, the run numbers in the high level photon stream format are not neccessary continues, since calibration runs are missing. The run integer in the file name is always 3 digits, e.g. ```20170201_021.phs.jsonl.gz``` is the twentyfirst run of the first night in February 2017.

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
- 1: External trigger input 1. Here the GPS module triggers the read out ```59``` times a minute. These events are expected to contain only night sky background.
- 2: External trigger input 2. The same as external trigger input 1, since the GPS modul was switched from 1 to 2 once.
- 1024: A random trigger also called "pedestal trigger". These events are also expected to only contain night sky background.

For a full overview of the FACT trigger types, see the [Phd of Patrick Vogler, table 4.3.b](http://e-collection.library.ethz.ch/eserv/eth:48381/eth-48381-02.pdf)

```json
"Az_deg":-63.253664797474336,"Zd_deg":33.06900475126648
```
The pointing direction of the FACT telescope in the moment the event was recorded. This is reconstructed from the ```aux``` (auxilluarry) drive files based on the event time.  ```"Az_deg"``` is the azimuth pointing in degrees, and ```"Zd_deg"``` is the zenith distance pointing in degrees.

```json
"PhotonArrivals_500ps":[[],[],[]]
```
The actual photon stream. A list of lists of arrival times of photons in units of ```500ps```.
The outer list loops over all ```1440``` pixels of FACT and is ordered in ```Continuous  Hardware ID (CHID)```. The inner lists loop over the arrival times of the individual photons for the corresponding pixel. The maximum number of photons in a pixel before the extraction of photons is aborted is ```500```. If there are ```500``` photons in a pixel, this pixel is __saturated__ and meaningless.
Since a single photon is now defined by only one sharp arrival time in contrast to a very long pulse, there is no need anymore to stick to a long region of interest in time and therefore the output of the photon-stream is truncated only to the region where the air-shower physics takes place, which is from ```15ns``` to ```65ns``` on FACT's common ROI. This is still rather long compared to e.g. the MAGIC telescope ROI of ```30ns```.

```json
"SaturatedPixels":[123,456]
```
A list of pixels in ```CHID``` to indicate that the corresponding pixel had an saturated analog time line out of the raw DRS4 chip. The maximim number of saturated pixels is ```100```, as the event is skipped then anyhow. Usually this list is empty. Such saturations happen not only for ultra high energy air showers, but also when the DRS4 calibration was not possible or is broken elseway. 

## Integration into existing air shower reconstruction software
When the idea of the photon-stream is inverted, the amplitude time lines of an individual pixel can be reconstructed from the photon-stream events which enables FACT to use ist usual air shower reconstruction programs right ahead without modifications.  
