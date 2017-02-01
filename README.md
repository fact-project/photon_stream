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
As a technology demonstrater, the FACT telescope records its observations in a data format which is as close to the read out hardware as possible. This was a great choice to explore the novel SIPM and DRS readout chain, but is rather tedious to do high level physics analysis as flux, spectra and light-curve investigations on the astronomical sources. These raw events are ```1440``` pixels x  ```300``` time slices x ```16```bit dynamic range = 864kB in size. They can not be analyzed independent of each other since readout artifacts can only be removed with knowledge on the previous event, and an additional calibration file for the DRS is needed, which is not straight forward to identify. Also huge effort was spent to compress the raw events with a dedicated format ```zfits```, the events shrunk only by a factor of about 3 down to about 290kB in size.

Now using the photon stream, we can compress events down to a size of 4.5kB for dark night events. Based on this, the idea was born to create a no compromise, only physics file format for the FACT telescope with the potential to fit all events from 2011 to 2017 will on a single hard disk drive of 10TB.

## Content of a Photon Stream Event

### Identification
- Night ID
- Run ID
- Event ID

### Timing
- The Unix time provided by the FACT event builder

### Telescope Pointing
- Azimuth angle
- Zenith distance angle

### Photon Arrivals
- A list (each pixel) of lists (each photon in a pixel) of arrival times of individual photons

### Artifacts and Detector
- A list of saturated pixels (usually empty)

## File Format
After evaluation of several formats (FITS, massage pack, JSON, custom binary), JSON-lines with gzip was chosen.
The following shows an example event in the final format:
```json
{"Night":20170119,"Run":229,"Event":1,"UnixTime_s_us":[1484895178,532244],"Trigger":4,"Az_deg":-63.253664797474336,"Zd_deg":33.06900475126648,"PhotonArrivals_500ps":[[59,84],[102,93,103],[58],[65,79,97],[],[125,43,68],[102],[68,100,123],[52,52,79,113,61,78,112,87], ... ],"SaturatedPixels":[]}
```
The run files will be named ```YYYYmmnn_RRR.phs.jsonl.gz```.
It turned out, that gzipped JSON-lines has only a size overhead of ```1.15``` compared to the smallest possible binary format we could come up with. Since the possibility for new students is pretty much ```0.0``` to read our custom binary, but almost ```1.0``` to read JSON-Lines, we decided to go with JSON-Lines for now.

```json
"Night"
```

The FACT night integer. 
